# 根据 docs/ 重新生成导航并构建站点。
# 文档源就是项目内的 docs/，不再从外部目录同步。
# Usage: powershell -ExecutionPolicy Bypass -File build.ps1
$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot
try {
    # 1. 根据 docs/ 目录结构重新生成导航
    python (Join-Path $PSScriptRoot "gen_zensical_config.py")
    if ($LASTEXITCODE -ne 0) {
        Write-Error "nav generation failed"
        exit $LASTEXITCODE
    }

    # 2. 构建静态站点
    # 注意：zensical 0.0.56 在 Windows 上 `--clean` 清理缓存时存在竞态，
    # 会偶发 panic（"cache directory could not be removed"）。这里改用普通构建，
    # 缓存由 zensical 自行增量维护；如需强制全量重建，手动删除 .cache/ 后重跑即可。
    python -m zensical build
    if ($LASTEXITCODE -ne 0) {
        Write-Error "build failed"
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}

Write-Host "Build done." -ForegroundColor Green