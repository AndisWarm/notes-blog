# 06 自救：常见报错 FAQ 与 PowerShell 坑

> 目标：报错时按"**现象 → 原因 → 处理**"三步查表，先自己救，救不了再求助。
> 本表按报错**原文**索引（原 `manual/07` 按业务分类，这里是按你屏幕上看到的话查）。
> 所有处理命令都是 **PowerShell** 版本。

## A. 终端 / 环境类

| 你看到的报错 | 原因 | 处理 |
|---|---|---|
| `node 不是内部或外部命令` / `无法识别"node"` | Node 没装好，或装完没重开终端（PATH 没刷新） | 重开一个终端；还不行就重装并勾选 "Add to PATH" |
| `go` 同样提示 | 同上（Go 装完默认在 Program Files，需重开终端） | 同上 |
| `npm ERR! network ... ETIMEDOUT` / 卡住不动 | 网络连不上 npm 官方源 | `npm config set registry https://registry.npmmirror.com` 后重跑 `npm install` |
| `无法加载文件 ... 因为在此系统上禁止运行脚本`（ExecutionPolicy） | PowerShell 执行策略限制脚本 | 项目脚本都要求带 `-ExecutionPolicy Bypass` 运行，照抄即可；自己跑 `.ps1` 时同样带上 |
| `curl : 无法将“curl”项识别为 cmdlet...` | PowerShell 5.1 里 `curl` 是旧别名 | 一律用 `curl.exe` |
| 在 PowerShell 里粘贴命令报各种奇怪语法错 | 原文档命令是 bash 语法 | 查 00 篇 0.5 对照表；openssl 类命令用 Git Bash |
| 启动脚本报"路径不存在" | 终端不在项目根目录 | `cd F:\毕业设计\韩师academic\ImageProvenanceV2` 后再跑 |
| `... already in use` / `EADDRINUSE`（端口占用） | 上次的服务窗口没关干净 | `netstat -ano \| findstr :8080` → 最后一列是 PID → `taskkill /PID 数字 /F` |

## B. 五窗口启动类

| 你看到的报错 | 原因 | 处理 |
|---|---|---|
| Hardhat 窗口没有 `Started HTTP...`，只有报错堆栈 | 端口 8545 被占，或 Node 版本问题 | 先杀残留进程（A 类）；确认 `node --version` ≥ 18 |
| 部署脚本报错/没打印合约地址 | ① 链没起，或链窗口已关 | 重新起 ①，再跑 ② |
| 后端日志没有 `chain listener started` | ② 没跑，或 `contracts/deployments/localhost.json` 缺失 | 重跑 ②，重启 ④ |
| 后端日志报 ABI/artifacts 相关错误 | 改过合约但没重新编译部署 | 在 `contracts` 下 `npx hardhat compile` → 重跑 ② → 重启 ④ |
| 前端黄条"链信息不可用——请先启动 Hardhat 并部署合约" | ① ② 没做，或 ④ 起得比 ② 早 | 补齐 ① ② → 重启 ④ → 刷新页面 |
| 前端页面能开但接口全红 | ④ 没起 | 起 ④ 后刷新 |
| 浏览器打开 5173 拒绝连接 | ⑤ 没起或已崩 | 看 ⑤ 窗口日志，重跑 |

## C. 登记 / 验证（页面或 curl 返回的）

| 报错原文 | 原因 | 处理 |
|---|---|---|
| `400 title is not valid UTF-8` | **Windows curl 用 GBK 发中文**，后端拒绝坏编码 | 用网页上传；或终端切 UTF-8：`chcp 65001` 后重试 |
| `409 already registered (xxx hash match)` | 同一文件（或其签名版/声明）已登记过 | 预期行为=防抢注；换文件；`matchTier` 字段告诉你撞了哪层 |
| `500 c2patool embed failed` | 证书/私钥不存在（首次没跑 make-ca.sh）或路径失效 | Git Bash 里 `bash tools/ca/make-ca.sh`，确认 `tools/ca/` 四件套在，重启后端 |
| `c2paStatus: "unavailable: ..."` | c2patool 找不到/不可执行 | `tools\bin\c2patool.exe --version` 手测；核对 `C2PATOOL_PATH` 环境变量 |
| `c2paStatus: "valid-untrusted"` | 信任锚没配或证书不匹配 | 核对 `C2PA_TRUST_ANCHORS` 指向 `tools/ca/rootCA.pem`；重新生成过证书后要重启后端 |
| `c2paStatus: "invalid"` | manifest 断言不合规（最常见：自己改过 manifest.go 后少了 `digitalSourceType`） | 还原 manifest.go 的断言结构；用 c2patool 看 validation_results 失败码定位 |
| 验证返回"无记录"，但明明登记过 | 传的不是登记时的**原字节**（截图/压缩/重存都会变哈希）；或改的是原图 | 用登记时那个文件原样上传；想演示"签名后被篡改"必须改**签名分发版**（04 篇 4.4） |
| 验证返回 source=chain | 本地索引没这条（删过库/绕过后端登记） | 非故障——链上反查兜底生效，反而值得在演示里讲 |

## D. MetaMask / 交易类

| 你看到的报错 | 原因 | 处理 |
|---|---|---|
| 交易一直 pending，不弹确认或确认后没反应 | **重启 Hardhat 后没清 nonce**——MetaMask 记着旧序号 | MetaMask → 设置 → 高级 → 清除活动与 nonce 数据 → 选该账户 |
| 弹窗报 `internal JSON-RPC error` / `cannot estimate gas` | 交易会被合约拒绝（如非作者操作），或链没起 | 看页面红色提示的中文原因；确认 ① 窗口还活着 |
| 点"② 钱包上链确权"没反应 | 没连钱包 / prepare 没成功 / 弹窗被浏览器拦截 | 先点"连接 MetaMask"；检查浏览器扩展弹窗权限 |
| 余额充了还是 0 | 网络或账户不对；或没出新块 | 确认 MetaMask 顶部是 Hardhat Local + 正确账户；点水龙头（它会自动补挖块） |
| 连接后 chainId 不是 31337 | 没切到本地网络 | 前端会自动请求切换；手动参数见 01 篇 1.5 表格 |
| `已在钱包中取消` | 你自己点了拒绝 | 重新操作即可，不是错误 |

## E. 授权 / 分账 / 状态标记类

| 你看到的报错 | 原因 | 处理 |
|---|---|---|
| "合约拒绝:当前钱包不是该作品的链上作者" | 用非作者账户操作（演示越权攻击时这是**预期结果**） | 切回作者账户 |
| 签发成功但记录迟迟不出现 | 监听器 2s 轮询 + 前端 3s 刷新 | 等 3–5 秒；还不出现查后端日志有没有 `chain listener started` |
| 撤销后表格没变化 | 同上（事件镜像延迟） | 刷新；超 10s 看后端日志 |
| 分账回显"读取失败" | 没装 MetaMask——**只读也要 window.ethereum 当 provider** | 装插件并连接 |
| 状态按钮点了没反应 | 没连钱包（按钮是 disabled 的） | 先连接 |

## F. 数据一致性类

| 你看到的报错 | 原因 | 处理 |
|---|---|---|
| 重启 Hardhat 后列表还有旧作品，但操作全失败 | 链清零而 SQLite 还在，旧记录的链上编号失效 | 删 `backend\data\index.db` → 重启后端（标准归零，01 篇 1.6） |
| 后端宕机期间上链的作品状态没更新 | 正常——监听器断了 | 重启后端等几秒，日志见 `anchored: chainWorkId=...` |
| 怀疑数据乱七八糟 | 任何原因 | 终极手段：停后端 → 删 index.db（或把 `chain_cursor.last_block` 置 0）→ 重启，全量重扫重建（幂等安全） |
| 日志出现 `anchored (no local row)` | 有人绕过后端直接调合约登记 | 非故障；该作品不入本地索引，但链上反查可验 |
| 测试脚本第二遍全挂 `invalid expiry` | 前一遍脚本用 `evm_increaseTime` 把链时间推前了 | 重启 Hardhat 再跑 |

## G. 证书 / C2PA 工具类

| 你看到的报错 | 原因 | 处理 |
|---|---|---|
| 生成的证书 Subject 是一串路径（`/C=CN/...` 被改） | Git Bash 的路径改写 | 项目脚本已内置 `MSYS_NO_PATHCONV=1`；**手敲 openssl 命令时自己加上** |
| `c2patool` 报 `trust_anchors` 是非法 URL | Windows 盘符路径（`C:\...`）被当 URL scheme | 后端已规避；手动操作时把锚文件路径写对或用相对路径 |
| `ipfs config` 参数被改写 | 同上（MSYS 路径改写） | 用 PowerShell 跑 ipfs，或加 `MSYS_NO_PATHCONV=1` |
| PDF 中文变问号/缺失 | 没配 `PDF_UNICODE_FONT` | 启动后端前 `$env:PDF_UNICODE_FONT = "C:\Windows\Fonts\simhei.ttf"`（start-backend.ps1 会自动探测，一般不用管） |
| PDF 二维码扫码打不开 | `VERIFY_BASE_URL` 与实际前端地址不符 | 按实际部署地址配置后端环境变量 |

## H. PowerShell 专属坑（原文档没提、小白必踩）

1. **粘贴命令多行错乱**：PowerShell 一次粘贴多行时逐行执行，若某行等号/引号没闭合会
   卡在 `>>` 续行提示——按 `Ctrl+C` 取消，重新整段粘贴。
2. **`$` 被解析**：命令里带 `$env:...` 是正常语法；若某条命令含 `$` 且报错
   变量不存在，说明该命令不是 PowerShell 风格，查 00 篇 0.5 对照。
3. **`findstr` 区分大小写**：`netstat -ano | findstr :8080` 里的冒号半角即可；
   换端口时注意别把别的数字也匹配进去。
4. **中括号/引号转义**：路径含中文没问题；路径含空格必须整体加引号。
5. **改了环境变量不生效**：环境变量改动只对**新开的终端**生效，改完重开窗口。
6. **后台任务杀不掉**：窗口直接关 = 进程可能还在（端口占用）。用 A 类的
   `netstat` + `taskkill` 按 PID 杀，别只关窗口。

## 救不了？按这个格式求助（三件套）

1. `/api/health` 完整输出（`curl.exe http://127.0.0.1:8080/api/health`）
2. 后端窗口最近 30 行日志
3. 复现步骤：哪个页面 / 哪个账户 / 点了什么 / 看到了什么

> 九成问题在这三样里已经有答案。`manual/07` 是原项目的完整故障手册（按业务分类，
> 每条带"根因 → 解法 → 原理出处"），本表查不到就去翻它。