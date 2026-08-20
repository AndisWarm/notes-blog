# 05 API 参考(小白版,带基础)

> 本篇目标:看懂"接口"是怎么回事,八个接口逐个读通,会照抄 curl 命令。
> 对照原手册 `manual/05-API参考.md` 阅读——本篇在它基础上加了 5.1(HTTP 基础)和 5.2(curl 基础)。
> 每个接口的 JSON 响应字段,本篇都用表格逐行解释。

---

## 5.1 先补两个基础:HTTP 和 JSON

### HTTP 是什么

网页和服务器说话用的"语言"。你(客户端)发一个**请求**,服务器回一个**响应**。
请求由四部分组成:

| 部分 | 例子 | 大白话 |
|---|---|---|
| 方法(Method) | `GET` / `POST` | 想干嘛:`GET`=查东西,`POST`=提交东西 |
| 路径(Path) | `/api/works/prepare` | 找谁办事 |
| 头(Headers) | `Content-Type: application/json` | 附加说明(比如"我发的是 JSON") |
| 体(Body) | 上传的文件、JSON 数据 | 要交给服务器的东西(仅 POST 常见) |

**状态码**:服务器用三位数答复,常见:

| 码 | 含义 | 在本系统什么时候见到 |
|---|---|---|
| 200 | 成功 | 几乎所有查询 |
| 201 | 创建成功 | `prepare` 登记成功 |
| 400 | 请求格式错 | 缺文件、中文标题编码错 |
| 404 | 找不到 | 查不存在的作品 ID |
| 409 | 冲突 | 重复登记同一文件 |
| 500 | 服务器内部错误 | 签名/存储/打包失败 |
| 503 | 服务暂不可用 | 链没配置 |

### JSON 是什么

一种"给计算机看的记事本格式":`{"字段": 值, "另一个字段": 值}`。
本系统所有接口都用 JSON 通信。读法很简单:**大括号是对象,方括号是数组,冒号左边是字段名右边是值**。

```json
{
  "status": "ok",          ← 字段 status,值是字符串 "ok"
  "chainId": 31337,        ← 字段 chainId,值是数字
  "items": [1, 2, 3]       ← 字段 items,值是数组
}
```

### curl 是什么

命令行里的"浏览器":用它直接从终端发 HTTP 请求。后面每个接口都配了 curl 示例,照抄即可。

**通用约定**(记住这三条,后面全按它走):

- 基地址:`http://127.0.0.1:8080`(就是后端,端口可用 `APP_PORT` 改);
- **无鉴权**:所有接口开放,不需要登录(本地演示定位;生产化需加鉴权与限流);
- CORS 全放开:前端跨端口直调,不用担心浏览器拦截;
- 错误统一格式:`{"error": "描述"}`;
- 时间格式:`createdAt` 是 RFC3339(UTC,如 `2026-07-26T12:00:00Z`);
  `validUntil` 是 Unix 秒(自 1970 年起的秒数,如 `1785150000`)。

---

## 5.2 接口一:GET /api/health(健康检查)

**用途**:确认后端活着、链连着、工具都在。

```powershell
curl http://127.0.0.1:8080/api/health
```

响应示例与逐字段解释:

```json
{
  "status": "ok",
  "storageBackend": "ipfs | local",
  "chainReady": true,
  "chainId": 31337,
  "signerMode": "creator-wallet",
  "c2patool": { "available": true, "path": "...", "version": "c2patool 0.27.3", "error": "仅失败时出现" },
  "c2paTrust": true
}
```

| 字段 | 含义 | 常见异常 |
|---|---|---|
| `status` | 后端存活标志 | 连不上=后端没起 |
| `storageBackend` | 当前存储模式 | — |
| `chainReady` | 链可达 + 部署文件已加载 | `false` = 链没起或没部署 |
| `chainId` | 链编号(31337=本地链) | — |
| `signerMode` | 恒为 `creator-wallet`(零私钥声明) | — |
| `c2patool.available` | C2PA 工具可用性 | `false` = 路径错 |
| `c2paTrust` | 信任锚是否配置 | `false` = 证书问题,验不出 Trusted |

## 5.3 接口二:GET /api/chain/info(合约地址与 ABI)

**用途**:前端/脚本拿到合约地址和 ABI,才能"知道该跟谁说话"。
ABI = 合约的"说明书"(每个函数叫什么、参数是什么),由 Hardhat 编译产物原样透传。

```powershell
curl http://127.0.0.1:8080/api/chain/info
```

```json
{
  "chainId": 31337,
  "network": "localhost",
  "registry": { "address": "0x...", "abi": [...] },
  "license":  { "address": "0x...", "abi": [...] },
  "royalty":  { "address": "0x...", "abi": [...] }
}
```

**错误**:`503 {"error":"chain not configured (deploy contracts first)"}` =
没部署合约(第 02 篇步骤 2 漏了),补部署后**重启后端**。

## 5.4 接口三:POST /api/chain/faucet(水龙头)

**用途**:给指定地址充 10 个测试 ETH(仅本地链 31337)。

```powershell
curl -X POST -H "Content-Type: application/json" -d '{"address":"0x70997970C51812dc3A010C7d01b50e0d17dc79C8"}' http://127.0.0.1:8080/api/chain/faucet
```

成功 200:

```json
{ "address": "0x...(小写)", "balanceWei": "10000000000000000000", "note": "local dev chain only; funded via hardhat_setBalance" }
```

| 字段 | 含义 |
|---|---|
| `balanceWei` | 余额,**单位是 Wei**(1 ETH = 10^18 Wei)。`10000000000000000000` = 10 ETH |
| `note` | 实现说明:走 `hardhat_setBalance` 直接改余额 |

**行为细节**:充值后自动**补挖一个空块**——这是为了"击穿钱包的按块高余额缓存"
(不然 MetaMask 显示的余额可能不刷新)。

**错误**:`400` 地址缺失/非法;`403` 非本地链(chainId≠31337);
`503` 链未配置。

## 5.5 接口四:POST /api/works/prepare(登记准备,核心接口)

**用途**:上传图片 → 算三哈希 → C2PA 签名 → 存 IPFS → 返回"待签名交易"。
这是全系统最复杂的接口,分三部分讲。

### 请求(multipart/form-data,即"表单上传")

| 字段 | 必填 | 说明 |
|---|---|---|
| `image` | 是 | PNG/JPEG 文件 |
| `title` | 否 | 缺省用文件名;**必须合法 UTF-8**(Windows curl 发中文会 GBK → 400) |
| `authorAddress` | 建议 | 创作者钱包地址,写入 C2PA 声明(链上作者最终以**交易签名者**为准) |

```powershell
curl -F "image=@a.png" -F "title=api-demo" -F "authorAddress=0x7099..." http://127.0.0.1:8080/api/works/prepare
```

### 成功 201 响应(分段解释)

```json
{
  "work": { "id": 7, "status": "PENDING_ANCHOR", "c2paStatus": "trusted",
            "originalHash": "0x…", "signedHash": "0x…", "manifestHash": "0x…",
            "imageCid": "…签名分发版CID…", "…其余字段见数据字典…": "" },
  "manifest": { "title": "…", "authorAddress": "0x…", "imageHash": "0x…",
                "createdAt": "…", "claims": { } },
  "txRequest": { "to": "0xRegistry", "data": "0x21679155…", "chainId": 31337 },
  "similarWarnings": [ { "workId": 6, "hammingDistance": 10 } ],
  "note": "存储说明",
  "timingsMs": { "hashAndManifest": 3, "phash": 2, "c2pa": 250, "ipfs": 5, "repository": 1, "total": 799 }
}
```

| 顶层字段 | 含义 |
|---|---|
| `work` | 链下作品记录(还未上链,所以 `status=PENDING_ANCHOR`) |
| `manifest` | 人类可读的声明内容(标题/作者/原图哈希/生成器) |
| `txRequest` | **待签名交易**:发给哪个合约(`to`)、什么数据(`data`)——由**创作者钱包**签名发送,后端不代签 |
| `similarWarnings` | pHash 相似预警列表(仅提示不拦截);`hammingDistance` 越小越像 |
| `note` | 存储说明(IPFS / local) |
| `timingsMs` | 每步耗时(毫秒)——性能排查时有用 |

### 错误

| 码 | 场景 |
|---|---|
| 400 | 缺 image / title 非 UTF-8 |
| 409 | 重复文件——响应含 `matchTier`(撞了三哈希中的哪个)与已登记的 `work` |
| 500 | 签名/存储/打包失败(看后端日志;常见 CA 证书问题,第 07 篇) |

**两个要点**:
1. `txRequest` 必须由**钱包**签名发送 → 这就是"后端零私钥"的落地方式;
2. c2patool 不可用时:`c2paStatus="unavailable: …"` 且**没有 txRequest**——
   没签名版就没法上链(登记降级继续,但不能确权)。

## 5.6 接口五:GET /api/works(作品列表)

**用途**:拉全部作品,按 id 倒序。

```powershell
curl http://127.0.0.1:8080/api/works
```

返回 Work 数组,每个元素含 `status` / `chainStatus` / `c2paStatus` 等全部字段
(字段字典见第 06 篇 4.1)。

## 5.7 接口六:GET /api/works/:id(作品详情,含授权记录)

**用途**:查单个作品 + 它的授权记录(授权管理页的数据源)。

```powershell
curl http://127.0.0.1:8080/api/works/1
```

```json
{ "work": { "…Work 全字段…": "" },
  "licenses": [ { "chainLicenseId": 1, "chainWorkId": 3, "licensor": "0x…",
                   "licensee": "0x…", "usage": "网页横幅", "validUntil": 1785150000,
                   "revoked": false, "txHash": "0x…", "createdAt": "…" } ] }
```

| 要点 | 说明 |
|---|---|
| `licenses` | 链上事件镜像(第 03 篇 3.2 讲过),按 `chainLicenseId` 升序 |
| 未上链作品 | `licenses` 恒为空数组 |
| 错误 | `400` id 非数字;`404` 不存在 |

## 5.8 接口七:POST /api/works/verify-file(四态验证)

**用途**:上传任意文件,得到鉴定结论。**恒返回 200**,结论在字段里。

```powershell
curl -F "image=@a.png" http://127.0.0.1:8080/api/works/verify-file
```

```json
{ "matched": true, "matchTier": "original | signed | manifest-only | none",
  "reason": "人话解释", "computedHash": "0x…",
  "source": "db | chain", "c2paState": "Trusted | Valid | Invalid",
  "work": { "…关联作品,含 chainStatus 供争议/撤销警示…": "" } }
```

| 字段 | 含义 |
|---|---|
| `matchTier` | 四态:original / signed / manifest-only / none(判定逻辑见第 06 篇 2.3) |
| `reason` | 人话解释(前端红/黄/绿提示就来自这里) |
| `computedHash` | 本次上传文件的哈希 |
| `source` | `db`=本地索引命中;`chain`=本地没查到、由链上 `getWorkByHash` 反查命中 |
| `c2paState` | C2PA 校验结果,仅 manifest 路径有意义 |

> **`source=chain` 是什么信号?** 本地索引(SQLite)丢了/没同步,但链上记录还在,
> 于是接口直接问链。这是"数据库可丢性"的直接证据——账本才是最终真相。

## 5.9 接口八:GET /api/works/:id/report.pdf(证据 PDF)

**用途**:下载取证材料。

```powershell
curl -o report.pdf http://127.0.0.1:8080/api/works/1/report.pdf
```

| 要点 | 说明 |
|---|---|
| 内容 | 三哈希、作者地址、双时间戳(区块 + RFC3161)、验证页二维码(`?workId=` 参数) |
| 中文渲染 | 需要 `PDF_UNICODE_FONT` 指向中文字体;缺失时自动回退 ASCII(中文变问号,属预期降级) |
| 错误 | 404 作品不存在 |

## 5.10 curl 速查(全量复制可用)

```powershell
# 健康检查
curl http://127.0.0.1:8080/api/health

# 合约地址(建议装 jq 后这样读,不装也行,直接看 JSON)
curl http://127.0.0.1:8080/api/chain/info | jq '.registry.address'

# 水龙头
curl -X POST -H "Content-Type: application/json" -d '{"address":"0x70997970C51812dc3A010C7d01b50e0d17dc79C8"}' http://127.0.0.1:8080/api/chain/faucet

# 登记(注意中文 title 会 400,见 1.4 节坑 1)
curl -F "image=@a.png" -F "title=api-demo" -F "authorAddress=0x7099..." http://127.0.0.1:8080/api/works/prepare

# 列表 / 详情
curl http://127.0.0.1:8080/api/works
curl http://127.0.0.1:8080/api/works/1

# 四态验证(只看结论字段)
curl -F "image=@a.png" http://127.0.0.1:8080/api/works/verify-file | jq '.matchTier,.reason'

# 证据 PDF
curl -o report.pdf http://127.0.0.1:8080/api/works/1/report.pdf
```

> **最后提醒两件事**:
> 1. 命令行传中文 title:确认终端按 UTF-8 发送(PowerShell 7 可
>    `$PSDefaultParameterValues['*:Encoding']='utf8'`);老 curl.exe 建议改走网页上传。
> 2. **上链一步无法用 curl 完成**——需要钱包私钥签名,这正是零私钥设计
>    (第 00 篇 0.3、第 03 篇 3.7)。