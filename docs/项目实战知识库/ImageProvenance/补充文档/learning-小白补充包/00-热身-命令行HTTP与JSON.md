# 00 热身：命令行、HTTP 与 JSON

> 目标：补上原文档默认你会、但你其实没接触过的三样东西——终端、curl、JSON。
> 学完你能看懂原 `learning/01` 里的所有命令行，并知道在 Windows 上该怎么变通。
> **全程不需要装任何新东西**，Windows 自带。

## 0.1 终端（PowerShell）入门

### 什么是终端

终端 = 一个"用文字跟电脑说话"的窗口。图形界面是点按钮，终端是敲命令按回车。
本项目所有启动、测试、观察都要在终端里做，所以先花十分钟熟悉它。

### 打开方式

- 在任意文件夹的地址栏（资源管理器顶部）输入 `powershell` 按回车 → 直接在该文件夹打开
- 或在开始菜单搜 "PowerShell" 打开 → 再用 `cd` 切换目录

### 必须会的 6 个命令

| 命令 | 作用 | 示例 |
|---|---|---|
| `pwd` | 显示当前在哪个文件夹（print working directory） | `pwd` |
| `ls` | 列出当前文件夹的内容 | `ls` |
| `cd 路径` | 切换文件夹 | `cd ..\..` 向上两级；`cd D:\abc` 直接跳盘符 |
| `Get-ChildItem` | 就是 `ls` 的完整名字，两者一样 | — |
| `Ctrl+C` | **停止当前正在跑的程序**（比如卡住的服务器） | — |
| `cls` / `clear` | 清屏 | — |

> **常用技巧**：在 PowerShell 里输入路径时按 `Tab` 键会自动补全；敲 `cd D:` 加 Tab
> 可以浏览盘符。鼠标选中文字 = 复制，**右键 = 粘贴**（这是 PowerShell 最反直觉但最有用的一点）。

### 什么是"路径"

电脑文件的地址。分两种：

```text
相对路径：从"当前所在文件夹"出发        例如 ..\..\contracts  （.. 表示上一级）
绝对路径：从盘符出发，写全            例如 F:\毕业设计\...\contracts
```

本项目脚本在 `F:\毕业设计\韩师academic\ImageProvenanceV2\`（下称**项目根目录**）。
所有启动命令都要求在**项目根目录**的终端里执行，否则找不到脚本文件。

### 什么是"环境变量"（先混个脸熟）

Windows 的一个"全局记事本"，存一些程序启动时要读的配置（比如 Go 安装在哪）。
安装软件时勾选 "Add to PATH" 就是在往这个记事本里写条目。
**你只需要知道**：装完 Node/Go 后**关掉所有已开的终端再重新开一个**，
新终端才能认出 `node`、`go` 这些命令。这是新手第一高频坑。

### 判断命令有没有装好

```powershell
node --version   # 输出版本号如 v22.x.x 就是装好了
go version       # 输出 go version go1.x.x windows/amd64
```

如果提示"无法识别"或"不是内部或外部命令" → 没装或没进 PATH（见 01 篇）。

## 0.2 HTTP 与 curl：用命令行发请求

### 本项目的基本对话方式

整个系统分成几个程序，程序之间用 **HTTP 请求**说话。HTTP 请求就是"问服务器要东西/让服务器做事"，
格式大致是：方法 + 网址 + 可选的数据。浏览器打开网页、点按钮，背后发的也是 HTTP 请求。

- 常见的"方法"：`GET`（取数据，不改变东西）、`POST`（提交数据，通常有副作用）
- 网址长这样：`http://127.0.0.1:8080/api/health`
  - `127.0.0.1` = 本机（你自己的电脑）
  - `8080` = 端口（同一台电脑上不同程序的"门牌号"）
  - `/api/health` = 路径（这个程序里的哪个接口）

### curl：终端里的浏览器

`curl` 就是"用命令行发 HTTP 请求"的工具。Windows 10/11 自带，不用装。

```powershell
# GET 请求：问后端"你健康吗"
curl http://127.0.0.1:8080/api/health

# POST 请求：传一个文件给后端（本项目登记作品就用这个）
curl -F "image=@D:\随便\一张图.png" -F "title=我的第一张图" http://127.0.0.1:8080/api/works/prepare
```

| 参数 | 含义 |
|---|---|
| `-X POST` | 显式指定方法（`curl` 默认是 GET；带 `-F` 时自动用 POST，可不写） |
| `-F "字段=值"` | 表单数据；`@路径` 表示"这个字段是一个文件"（`@` 不能丢） |
| `-H "..."` | 自定义请求头（后面查链时用） |
| `-d "{...}"` | 发送 JSON 正文（后面查链时用） |

### 小白第一坑：curl 和 Windows 内置的 `curl.exe`

PowerShell 里直接敲 `curl` 有两种可能：

- PowerShell 5.1 里，`curl` 其实是 `Invoke-WebRequest` 的**别名**，语法完全不同，会报错
- 新版 PowerShell（7+）和 Windows 10 1803+ 里，`curl` 指向真正的 `curl.exe`

**保险写法**：一律敲 `curl.exe`。本项目文档里凡是 `curl` 开头的命令，在 PowerShell 里都
可以（也应该）写成 `curl.exe`。

```powershell
curl.exe http://127.0.0.1:8080/api/health     # 永远可用
```

## 0.3 JSON：服务器回答你的语言

JSON 是服务器返回数据的通用格式，就是"带引号的键值对嵌套"：

```json
{
  "status": "ok",
  "chainId": 31337,
  "works": [
    { "id": 1, "title": "我的第一张图" }
  ]
}
```

- `{ }` 包一个对象，`[ ]` 包一个数组（列表）
- 键和字符串值必须带**英文双引号**
- 读法：`status 是 ok`、`works 是一个数组，数组里第一个元素的 title 是 我的第一张图`

**实操**：跑通系统后执行 `curl.exe http://127.0.0.1:8080/api/health`，
试着在返回的 JSON 里找到 `status` 和 `chainId` 两个字段。这就是原 learning/01 让你
"逐字段读懂"的东西。

### 中文乱码

如果 curl 返回的中文是 `\uXXXX`（反斜杠 u 加数字），不是坏了——那是 JSON 的 Unicode 转义，
表示的是中文字符。浏览器地址栏访问同样的地址会显示正常中文。也可以用
`curl.exe ... | ConvertFrom-Json | ConvertTo-Json -Depth 5` 让 PowerShell 帮你转成可读格式。

## 0.4 端口占用：发现"有程序占着门牌号"

启动报错里最常见的：`port 8080 is already in use`（8080 端口已被占用）。
意思是有一个上次没关干净的程序还占着 8080。查找并结束它：

```powershell
# 找到占用 8080 端口的进程号（PID）
netstat -ano | findstr :8080
# 输出类似：  TCP    0.0.0.0:8080   0.0.0.0:0    LISTENING    12345
# 最后一列 12345 就是 PID

# 结束它（把 12345 换成你查到的数字）
taskkill /PID 12345 /F
```

> 如果 `netstat` 输出为空，说明端口没被占，问题在别处（去查 06 篇）。

## 0.5 原文档里的 bash 命令，在 Windows 上怎么办

原 `learning/` 很多命令是 Linux bash 语法，Windows PowerShell 不能直接跑。对照表：

| 原文档写法（bash） | PowerShell 写法 | 说明 |
|---|---|---|
| `sha256sum a.txt` | `Get-FileHash a.txt -Algorithm SHA256` | 结果多了 `Hash`、`Path` 两列，取 `Hash` 那列（小写化）即可 |
| `echo hello > a.txt` | `Set-Content -Path a.txt -Value "hello"` | 写入文件 |
| `cat a.txt` | `Get-Content a.txt` | 读文件（在 IDE 里看更简单） |
| `command > out.txt` | `command *> out.txt` 或 `command > out.txt 2>&1` | 输出重定向 |
| `grep 关键字 文件` | `Select-String -Path 文件 -Pattern "关键字"` | 在文件里搜文字 |
| `<(...)` 进程替换 | 不支持 | 原 learning/03 验签命令要用 Git Bash 跑，见 03 篇 |
| `$?` 判断上一条命令成败 | `$LASTEXITCODE` | 0 = 成功，非 0 = 失败 |
| `export A=B` | `$env:A = "B"` | 设环境变量（仅当前终端） |
| `openssl` | 同 `openssl`（Git Bash 自带；PowerShell 里需另装） | 见 03 篇 |

**两个策略**：
1. 能变通的用上表变通（哈希、文件操作）；
2. 变通不了的（openssl 签名验签、make-ca.sh），**直接用 Git Bash 跑原命令**——项目脚本
   本身也是这么设计的（`tools/ca/make-ca.sh` 明确要求 Git Bash）。

Git Bash 打开方式：开始菜单搜 "Git Bash"，或在项目根目录右键 → "Open Git Bash here"。

## 回到正片

你现在能开终端、发 curl、读懂 JSON 了。回原 `learning/01`，里面所有命令在 PowerShell
里把 `curl` 换成 `curl.exe` 即可照跑。卡在环境安装就先看本包 `01-保姆级-环境搭建与五窗口启动.md`。