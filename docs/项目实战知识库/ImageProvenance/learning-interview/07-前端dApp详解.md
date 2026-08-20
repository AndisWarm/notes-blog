# 07 前端 dApp 详解：钱包、交易与读写分离

> dApp 前端与普通 Web 前端的三大差异：**钱包即身份、交易即写操作、链即数据库**。

## 7.1 文件地图

```
web/src/
├── composables/
│   ├── useWallet.js      钱包连接/网络切换/余额/发交易 (96 行，先读)
│   └── useContracts.js   合约实例工厂：签名版 + 只读版
├── api/
│   └── client.js         后端 REST 封装
├── views/
│   ├── CreatorView.vue   两步上链
│   ├── LicenseView.vue   授权/分账/状态（写操作最全）
│   └── VerifyView.vue    四态验证展示（纯读）
├── App.vue               壳：导航 + 钱包面板 + 水龙头
└── main.js               入口
```

## 7.2 useWallet：钱包是怎么被"接上"的

### 核心概念：window.ethereum

MetaMask 注入页面的 Provider，遵循 **EIP-1193** 标准接口。

```javascript
// 连接钱包四步
async function connect(expectedChainId) {
    // 1. 请求账户（触发弹窗）
    const accounts = await window.ethereum.request({ 
        method: 'eth_requestAccounts' 
    });
    
    // 2. 读链 ID
    const network = await provider.getNetwork();
    
    // 3. 不对则切换链
    if (state.chainId !== expectedChainId) {
        await switchChain(expectedChainId);
    }
    
    // 4. 挂监听
    window.ethereum.on('accountsChanged', ...);
    window.ethereum.on('chainChanged', () => window.location.reload());
}
```

### 身份差异

> **没有登录接口、没有 token**——"当前账户"就是身份，切账户 = 切身份，页面所有权限表现随之变。

## 7.3 txRequest 模式（本项目前后端协作的灵魂）

```
后端：abi.Pack(registerWork, ...) → {to, data, chainId}
                                      │
                                      ▼
前端：signer.sendTransaction({to, data}) → MetaMask 弹窗 → 用户确认 → 链
```

**知识与权力分离**：
- 后端懂 ABI 但**没有私钥**
- 前端不懂业务参数打包但**持有签名权**

### 为什么登记走后端，授权直接前端调？

| 操作 | 路径 | 原因 |
|------|------|------|
| 登记上链 | 后端 prepare → 前端发交易 | 三哈希、CID 只有后端算得出来 |
| 授权签发 | 前端直接调合约 | 参数用户表单里都有，不需要后端计算 |

**面试话术**：
> "登记的参数——三哈希、CID——只有后端算得出来，所以走后端打包；授权的参数用户表单里都有，前端直接调合约更直接。"

## 7.4 useContracts：读写分离的两个工厂

```javascript
// 写操作：需要签名，会触发授权弹窗
async function contract(which) {
    const { getSigner } = useWallet();
    const signer = await getSigner();  // ← 要求已连接钱包
    return new Contract(meta.address, meta.abi, signer);
}

// 只读操作：eth_call，无需连接钱包、无弹窗
async function readContract(which) {
    const provider = new BrowserProvider(window.ethereum);
    return new Contract(meta.address, meta.abi, provider);  // ← 只用 provider
}
```

**关键区别**：
- `contract()`：走 signer，可发交易，**要求已连接钱包**
- `readContract()`：走 provider，只读，**无需连接钱包、无弹窗**

**应用**：分账规则回显用 `readContract`，页面刷新后数据还在——因为每次都从链上读，后端数据库根本没存它。

## 7.5 LicenseView 精读（写操作全集）

### 四块功能

| 功能 | 合约调用 | 事件等待 |
|------|---------|---------|
| 签发授权 | `grantLicense` | 3秒后 refresh（等事件镜像） |
| 撤销授权 | `revokeLicense` | 同上 |
| 设置分账 | `setRoyaltyRule` | 即时回显（读链上） |
| 状态标记 | `setStatus` | 同上 |

### 两个通用模式

**1. revertReason 翻译**

```javascript
catch (err) {
    if (err.shortMessage?.includes('not author')) {
        error.value = '当前钱包不是该作品的链上作者，操作被合约拒绝';
    }
}
```

ethers 从 revert data 解码出 reason 字符串——链上 require 的 reason 一路穿透到 UI。

**2. 乐观等待**

```javascript
await tx.wait();
setTimeout(refresh, 3000);  // 等事件镜像
```

链上已成功、链下稍后到——这是事件驱动架构在 UI 层的自然形态。

## 7.6 缓存坑：钱包余额"刷不出来"

**现象**：水龙头充值后，MetaMask 界面余额纹丝不动。

**定位**：后端日志显示钱已到账。

**根因**：
- `hardhat_setBalance` 直改状态**不出块**
- MetaMask/ethers **以区块高度为缓存键**
- 不出新块，钱包界面永远刷不出新余额

**修复**：
```go
// 充值后补挖空块击穿缓存
return c.Eth.Client().CallContext(ctx, nil, "evm_mine")
```

**沉淀**：理解客户端缓存失效机制比改 UI 重要。

## 7.7 实验：观察弹窗差异

**实验 B**：分账卡片选中作品即回显规则（无弹窗），点"设置分账"才弹窗。

在 Network 面板分别找到：
- 回显：`eth_call`（只读，不走签名）
- 设置：`eth_sendRawTransaction`（写操作，需签名）

**确认**：读写走的 RPC 方法不同。

## 7.8 身份切换的 UI 表现

同一作品，甲/乙账户各看一遍授权管理页——**UI 完全一样**（按钮都可点），差别在点下去之后。

**讨论**：前端要不要在按钮层就判断"当前账户不是作者则禁用"？

| 方案 | 优点 | 缺点 |
|------|------|------|
| 禁用按钮 | 体验更好 | 前端判断可被绕过（直接调合约） |
| **可点但 revert（本项目）** | 权限的真相在链上 | 用户点了才知道不行 |

**面试话术**：
> "两边都对，讲出权衡即可。前端禁用是体验优化，链上校验是安全底线。本项目选择让用户点了再 revert，配合清晰的错误提示。"

## 7.9 前端技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| 框架 | Vue 3 | Composition API，响应式 |
| 路由 | Vue Router | 三视图：创作者/授权/验证 |
| 链交互 | ethers v6 | BrowserProvider 包 MetaMask |
| 构建 | Vite | 快，HMR |
| 样式 | 原生 CSS | 无框架依赖，轻量 |

## 7.10 面试高频追问

**Q: 为什么用 ethers 而不是 web3.js？**
> ethers 更轻量、API 更现代（Promise 化）、TypeScript 支持更好、文档更清晰。v6 的 BrowserProvider 对 EIP-1193 支持更标准。

**Q: 合约地址硬编码在前端吗？**
> 不。从 `/api/chain/info` 动态获取（hardhat artifacts 透传），重新部署不改前端。

**Q: 私钥存在前端吗？**
> 不。私钥在 MetaMask 里，前端只通过 Provider 请求签名，永远接触不到私钥。