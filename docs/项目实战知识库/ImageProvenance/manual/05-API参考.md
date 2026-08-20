# 05 API 参考

- 基地址:`http://127.0.0.1:8080`(`APP_PORT` 可改)。
- **无鉴权**:所有接口开放(本地演示定位;生产化需加鉴权与限流,见威胁模型残余风险)。
- CORS:全放开(`*`),前端跨端口直调。
- 错误统一格式:`{"error": "描述"}`;字段字典见 [`06-状态对照与数据字典.md`](06-状态对照与数据字典.md)。
- 时间:createdAt 为 RFC3339(UTC);validUntil 为 Unix 秒。

## GET /api/health — 健康检查

```json
{
  "status": "ok",
  "storageBackend": "ipfs | local",
  "chainReady": true,
  "chainId": 31337,
  "signerMode": "creator-wallet",
  "c2patool": { "available": true, "path": "...", "version": "c2patool 0.27.3", "error": "仅失败时" },
  "c2paTrust": true
}
```
`chainReady=false` 常见于链未启动或部署文件缺失;`signerMode` 恒为 creator-wallet(后端零私钥声明)。

## GET /api/chain/info — 合约地址与 ABI

```json
{ "chainId": 31337, "network": "localhost",
  "registry": { "address": "0x...", "abi": [...] },
  "license":  { "address": "0x...", "abi": [...] },
  "royalty":  { "address": "0x...", "abi": [...] } }
```
ABI 来自 hardhat artifacts 原样透传——前端/脚本据此构建合约实例,不要硬编码。
`503 {"error":"chain not configured (deploy contracts first)"}`:先部署合约再重启后端。

## POST /api/chain/faucet — 本地水龙头

请求 `{"address": "0x..."}`(JSON)。成功 200:
```json
{ "address": "0x...(小写)", "balanceWei": "10000000000000000000", "note": "local dev chain only; funded via hardhat_setBalance" }
```
行为:充值 10 测试 ETH 后**补挖一个空块**(击穿钱包的按块高余额缓存)。
错误:`400` address 缺失或非法;`403` 非本地链(chainId≠31337,公共测试网请用公共水龙头);
`503` 链未配置。

## POST /api/works/prepare — 登记准备(核心接口)

multipart/form-data:

| 字段 | 必填 | 说明 |
|---|---|---|
| image | 是 | PNG/JPEG 文件 |
| title | 否 | 缺省用文件名;**必须合法 UTF-8**(Windows curl 发中文会 GBK → 400) |
| authorAddress | 建议 | 创作者钱包地址,写入 C2PA 声明(链上作者最终以交易签名者为准) |

成功 `201`:
```json
{
  "work": { "id": 7, "status": "PENDING_ANCHOR", "c2paStatus": "trusted",
            "originalHash": "0x…", "signedHash": "0x…", "manifestHash": "0x…",
            "imageCid": "…签名分发版CID…", "…其余字段见数据字典…": "" },
  "manifest": { "title": "…", "authorAddress": "0x…", "imageHash": "0x…", "createdAt": "…", "claims": { } },
  "txRequest": { "to": "0xRegistry", "data": "0x21679155…", "chainId": 31337 },
  "similarWarnings": [ { "workId": 6, "hammingDistance": 10 } ],
  "note": "存储说明",
  "timingsMs": { "hashAndManifest": 3, "phash": 2, "c2pa": 250, "ipfs": 5, "repository": 1, "total": 799 }
}
```
要点:`txRequest` 由**创作者钱包**签名发送(后端不代签,无 tx 相关私钥);
`similarWarnings` 仅提示不拦截;c2patool 缺失时 `c2paStatus="unavailable: …"` 且**无 txRequest**。

错误:`400` 缺 image / title 非 UTF-8;
`409` 重复文件——响应含 `matchTier`(撞了三元组中哪个哈希)与已登记 `work`;
`500` 签名/存储/打包失败(看后端日志,常见为 CA 证书路径,见 07 排查手册)。

## GET /api/works — 作品列表

返回 Work 数组(按 id 倒序),含 `status` / `chainStatus` / `c2paStatus` 等全部字段。

## GET /api/works/:id — 作品详情(含授权记录)

```json
{ "work": { …Work 全字段… },
  "licenses": [ { "chainLicenseId": 1, "chainWorkId": 3, "licensor": "0x…", "licensee": "0x…",
                   "usage": "网页横幅", "validUntil": 1785150000, "revoked": false,
                   "txHash": "0x…", "createdAt": "…" } ] }
```
`licenses` 是链上事件镜像(授权管理页/验证页的记录数据源),按 chainLicenseId 升序;
未上链作品恒为空数组。`400` id 非数字;`404` 不存在。

## POST /api/works/verify-file — 四态验证

multipart:`image`(必填)。恒 `200`(结论在字段里):
```json
{ "matched": true, "matchTier": "original | signed | manifest-only | none",
  "reason": "人话解释", "computedHash": "0x…",
  "source": "db | chain", "c2paState": "Trusted | Valid | Invalid",
  "work": { …关联作品,含 chainStatus 供争议/撤销警示… } }
```
判定优先级与含义见 `06` 第二节③;`source=chain` 表示本地索引未命中、由链上
`getWorkByHash` 反查(数据库可丢性的直接证据)。

## GET /api/works/:id/report.pdf — 证据 PDF

`200 application/pdf`(inline)。内容:三哈希、作者地址、双时间戳(区块 + RFC3161)、
验证页二维码(`VERIFY_BASE_URL?workId=`)。中文渲染需 `PDF_UNICODE_FONT`,缺失自动回退
ASCII 过滤。`404` 作品不存在。

## curl 速查

```bash
curl http://127.0.0.1:8080/api/health
curl http://127.0.0.1:8080/api/chain/info | jq '.registry.address'
curl -X POST -H "Content-Type: application/json" -d '{"address":"0x70997970C51812dc3A010C7d01b50e0d17dc79C8"}' http://127.0.0.1:8080/api/chain/faucet
curl -F "image=@a.png" -F "title=api-demo" -F "authorAddress=0x7099..." http://127.0.0.1:8080/api/works/prepare
curl http://127.0.0.1:8080/api/works
curl http://127.0.0.1:8080/api/works/1
curl -F "image=@a.png" http://127.0.0.1:8080/api/works/verify-file | jq '.matchTier,.reason'
curl -o report.pdf http://127.0.0.1:8080/api/works/1/report.pdf
```

> 提醒:命令行传**中文** title 请确保终端按 UTF-8 发送(PowerShell 7 可
> `$PSDefaultParameterValues['*:Encoding']='utf8'`;老 curl.exe 建议改走网页上传)。
> 上链一步无法用 curl 完成——需要钱包私钥签名,这正是零私钥设计(参见 learning/01 1.3)。
