# 07 精读:前端 dApp 交互

**学习目标**:掌握 dApp 前端与普通 Web 前端的三大差异——钱包即身份、交易即写操作、
链即数据库;能讲清 txRequest 模式;完成一个小改动并验证。

**文件地图**(共 7 个业务文件,一晚上能读完):

```text
web/src/
  composables/useWallet.js     钱包连接/网络切换/余额/发交易(96 行,先读)
  composables/useContracts.js  合约实例工厂:签名版 + 只读版(第二读)
  api/client.js                后端 REST 封装(普通 fetch,扫一眼)
  App.vue                      壳:导航 + 钱包面板 + 水龙头
  views/CreatorView.vue        两步上链
  views/LicenseView.vue        授权/分账/状态(写操作最全,精读)
  views/VerifyView.vue         四态验证展示(纯读)
```

## 7.1 useWallet:钱包是怎么被"接上"的

- `window.ethereum` 是 MetaMask 注入页面的 Provider(EIP-1193 标准接口);
  ethers 的 `BrowserProvider` 把它包装成自己的 Provider 抽象。
- `connect()` 四步:请求账户(eth_requestAccounts,触发弹窗)→ 读链 ID → 不对则
  `wallet_switchEthereumChain`(没有该网络时 code 4902 → `wallet_addEthereumChain`
  自动帮用户添加 Hardhat Local)→ 挂 accountsChanged/chainChanged 监听。
- **身份差异**:没有登录接口、没有 token——"当前账户"就是身份,切账户=切身份,
  页面所有权限表现随之变(第 01 章你切乙账户时看到的一切)。

## 7.2 txRequest 模式(本项目前后端协作的灵魂)

```text
后端:abi.Pack(registerWork, ...) → {to, data, chainId} ─┐
前端:signer.sendTransaction({to, data}) → MetaMask 弹窗 → 用户确认 → 链
```

后端懂 ABI 但没有私钥;前端不懂业务参数打包但持有签名权——**知识与权力分离**。
读 `CreatorView.onAnchor()` + `useWallet.sendTransaction()` 串起来,再回看第 05 章 5.2②。

对比另一条路径:LicenseView 的授权/分账/状态操作**不经过后端**——
`useContracts.contract()` 用 ABI(从 `/api/chain/info` 动态拉取)+ signer 直接调合约。
**思考**:为什么登记要走后端打包,而授权直接前端调?(登记的参数——三哈希、CID——
只有后端算得出来;授权的参数用户表单里都有。)

## 7.3 useContracts:读写分离的两个工厂

- `contract(which)`:`getSigner()` → 可发交易,**要求已连接钱包**(会触发授权弹窗);
- `readContract(which)`:只用 `BrowserProvider` 不取 signer → eth_call 只读,
  **无需连接钱包、无弹窗**——分账规则回显用的就是它。
- 地址与 ABI 全部来自后端 `/api/chain/info`(hardhat artifacts 透传),前端零硬编码:
  重新部署不改前端。验证:改 `contracts/deployments/localhost.json` 里 Registry 地址
  再刷新页面,看报错来源。

回答第 01 章观察任务 4 的悬念:分账规则刷新后还在,因为回显数据**每次都从链上读**
(hasRule/getRoyaltyRule),后端数据库根本没存它。

## 7.4 LicenseView 精读(写操作全集)

按四块读:签发授权(grantLicense + 3 秒后 refresh——为什么要等?第 06 章答案)、
撤销、分账(setRoyaltyRule + `loadRoyaltyRule()` 即时回显)、状态标记(setStatus 三按钮,
按当前状态隐藏无意义按钮)。两个通用模式:

- **revertReason 翻译**:`err.shortMessage` 里含 `not author` → 中文提示。
  ethers 从 revert data 解码出 reason 字符串——链上 require 的 reason 一路穿透到 UI;
- **乐观等待**:交易确认后 `setTimeout(refresh, 3000)` 等事件镜像——
  链上已成功、链下稍后到,这是事件驱动架构在 UI 层的自然形态(生产可换轮询/推送)。

## 7.5 动手实验

**实验 A(必做,15 分钟)**:VerifyView 按 ID 查询的表格里没有"存储后端"这一行——
加上它:`<tr><th>存储后端</th><td>{{ workDetail.work.storageBackend || '—' }}</td></tr>`,
刷新看效果。体会"后端 JSON 字段 → 前端展示"的最短路径(数据早就在接口里,只是没展示)。

**实验 B(观察弹窗差异)**:分账卡片选中作品即回显规则(无弹窗),点"设置分账"才弹窗——
在 Network 面板分别找到对应的 eth_call 和 eth_sendRawTransaction,确认读写走的 RPC 方法不同。

**实验 C(切换身份看世界)**:同一作品,甲/乙账户各看一遍授权管理页——
UI 完全一样(按钮都可点),差别在点下去之后。**讨论**:前端要不要在按钮层就判断
"当前账户不是作者则禁用"?(体验更好 vs 权限的真相在链上、前端判断可被绕过——
两边都对,讲出权衡即可。)

## 自测

1. txRequest 模式下,前后端各自"知道什么、不知道什么"?这个分工防住了什么?
2. 登记走后端、授权走前端直调合约——判断标准是什么?再举一个"该走后端"的假想操作。
3. `readContract` 和 `contract` 的本质区别?分账回显为什么必须用前者?
4. "授权已上链,等待事件同步…"这句提示对应的系统事实链是什么(从 MetaMask 确认到表格出现)?
5. MetaMask 里"清除活动与 nonce 数据"解决的是什么问题?什么操作之后必须做?
