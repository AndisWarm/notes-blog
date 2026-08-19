# Watch the study notes directory and auto-sync on changes.
# Usage: powershell -ExecutionPolicy Bypass -File watch.ps1
$src = "F:\知识库\豆瓣读书\学习笔记"
$sync = Join-Path $PSScriptRoot "sync.ps1"

if (-not (Test-Path $src)) {
    Write-Error "Watch directory not found: $src"
    exit 1
}

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $src
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

Write-Host "开始监听目录：$src （按 Ctrl+C 退出）" -ForegroundColor Cyan

while ($true) {
    $result = $watcher.WaitForChanged([System.IO.WatcherChangeTypes]::All)
    if ($result.TimedOut) { continue }
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] 检测到变更，稍后同步..." -ForegroundColor Yellow
    # 防抖：等待 2 秒让连续的文件操作稳定下来
    Start-Sleep -Seconds 2
    & powershell -ExecutionPolicy Bypass -File $sync
}