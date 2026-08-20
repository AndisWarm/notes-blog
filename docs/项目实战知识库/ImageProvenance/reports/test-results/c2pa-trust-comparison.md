# C2PA 信任链对照证据（M2）

> 同一张自建证书签名的图片 tmp/smoke-signed.png，两种验证方式的结果对比。
> 生成时间：2026-07-26  工具：c2patool 0.26.68  证书：tools/ca/（ES256, EKU=emailProtection）

## 1. 默认信任列表（不认自建 CA）→ untrusted
```
    {
      "code": "signingCredential.untrusted",
      "url": "self#jumbf=/c2pa/urn:c2pa:c55adc31-e149-4bb8-b601-540aa29a4835/c2pa.signature",
      "explanation": "signing certificate untrusted"
    }
--
        {
          "code": "signingCredential.untrusted",
          "url": "self#jumbf=/c2pa/urn:c2pa:c55adc31-e149-4bb8-b601-540aa29a4835/c2pa.signature",
          "explanation": "signing certificate untrusted"
        }
```

## 2. 加载自建 Root CA 作为 trust anchor → Trusted

命令：`c2patool smoke-signed.png trust --trust_anchors tools/ca/rootCA.pem`
```
        {
          "code": "signingCredential.trusted",
          "url": "self#jumbf=/c2pa/urn:c2pa:c55adc31-e149-4bb8-b601-540aa29a4835/c2pa.signature",
          "explanation": "signing certificate trusted, found in System trust anchors"
        },
  "validation_state": "Trusted"
```

## 结论

信任判定完全由验证方持有的信任列表决定：同一签名，列表外 untrusted、列表内 Trusted。
论文口径：demo CA 等价于联盟场景下的平台方 CA；生产环境应替换为 C2PA 官方信任列表成员证书。
