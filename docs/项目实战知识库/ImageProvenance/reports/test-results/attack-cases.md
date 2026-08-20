# 攻击用例测试报告（论文第 5 章素材）

> 二期区别于常规"只测正常路径"的差异化测试设计：每个安全属性都配一个主动攻击用例。
> 两级验证：合约单元测试（`contracts/test/`，Hardhat）+ 全链路 E2E（`scripts/dev/e2e-demo.mjs`，真实后端与链）。

## 用例一：抢注攻击（重复哈希注册）

**威胁**：攻击者看到他人作品（或链上事件里的哈希）后抢先/重复注册，制造权属混乱。
**防御**：RegistryV2 `hashIndex` 对三元组每个哈希唯一约束；后端 prepare 前置 409 拦截。
**结果**：
- 单测：同 originalHash / signedHash / manifestHash 分别复用注册 → `duplicate: * hash` revert（3 例全过）；
- E2E：另一账户重放同一 calldata → 交易 revert；同文件再次 prepare → HTTP 409。

## 用例二：越权授权

**威胁**：任何人给任意作品（甚至不存在的作品）签发授权 —— 一期的真实漏洞。
**防御**：LicenseV2 `grantLicense` 强制 `registry.authorOf(workId) == msg.sender`，且 `workExists` 先行。
**结果**：
- 单测：非作者授权 → `not author` revert；幽灵 workId → `work not found` revert；
- E2E：账户 B 对账户 A 的作品 grantLicense → revert；作者本人授权成功且 3.5s 内镜像到链下索引。

## 用例三：越权分账

**威胁**：任何人覆盖他人作品的分账规则（一期真实漏洞：还可随意改写）。
**防御**：RoyaltyV2 同样经 `authorOf` 校验；仅作者可设置与更新。
**结果**：单测中攻击者 setRoyaltyRule → `not author` revert，原规则字段不变（断言校验）。

## 用例四：授权失效路径

**威胁**：过期/被撤销的授权仍被当作有效凭证使用。
**防御**：`isLicensed` 链上判断 `!revoked && validUntil > block.timestamp`。
**结果**：单测中 time.increaseTo 越过过期时间 → false；revoke 后 → false；非授权人 revoke → `not licensor` revert。

## 用例五：签名后篡改检测

**威胁**：拿到官方签名图后修改内容再传播。
**防御**：三元组验证 + C2PA hard binding 双层。
**结果**（E2E + 手测）：
- 篡改签名图 1 字节 → 三哈希全不命中，但文件内 manifest 仍可提取 → 判定 `manifest-only`（"签名后被篡改"），c2patool validation_state = **Invalid**；
- 篡改无 manifest 的原图 → 判定 `none`（未登记/已被破坏性处理）。

## 用例六：链下索引丢失

**威胁**：本地数据库损坏/丢失后"链上可验证"变成空话（一期架构的实际风险：链上无反查索引）。
**防御**：`getWorkByHash` 链上反查；verify-file 在 DB miss 时自动回退链上查询（结果标注 `source: chain`）。
**结果**：代码路径经 E2E 环境验证（DB 命中时走 db，逻辑分支单测覆盖）。

## 汇总

| # | 攻击 | 防线 | 合约单测 | E2E |
|---|---|---|---|---|
| 1 | 抢注/重复注册 | hashIndex 唯一 + 409 | ✅ | ✅ |
| 2 | 越权授权 | authorOf 校验 | ✅ | ✅ |
| 3 | 越权分账 | authorOf 校验 | ✅ | — |
| 4 | 过期/撤销授权 | isLicensed 链上判断 | ✅ | — |
| 5 | 签名后篡改 | 三元组 + hard binding | — | ✅ |
| 6 | 索引丢失 | 链上反查兜底 | — | 分支覆盖 |

合约测试：20 passing，coverage 98.55%（`contracts/coverage/`）。
E2E：15/15 passing（local 与 ipfs 两种存储模式各跑通一轮）。
