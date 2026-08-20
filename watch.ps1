# 监听 docs/ 目录，改动后自动重新生成导航并构建站点。
# Usage: powershell -ExecutionPolicy Bypass -File watch.ps1
$src = Join-Path $PSScriptRoot "docs"
$build = Join-Path $PSScriptRoot "build.ps1"

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
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] 检测到变更，稍后构建..." -ForegroundColor Yellow
    # 防抖：等待 2 秒让连续的文件操作稳定下来
    Start-Sleep -Seconds 2
    & powershell -ExecutionPolicy Bypass -File $build
}