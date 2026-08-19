# Sync study notes into this site's docs directory.
# 只同步「面试知识库」子目录，保留博客自身的定制文件（stylesheets/javascripts/assets/README.md）。
# Usage: powershell -ExecutionPolicy Bypass -File sync.ps1
$ErrorActionPreference = "Stop"

$src = "F:\知识库\豆瓣读书\学习笔记\面试知识库"
$dst = Join-Path $PSScriptRoot "docs\面试知识库"

if (-not (Test-Path $src)) {
    Write-Error "Source directory not found: $src"
    exit 1
}

# /MIR mirrors the source (removes extra files in dst).
robocopy $src $dst /MIR /XD node_modules .git /XF *.tmp *.temp *.log /NFL /NDL /NJH /NP

$code = $LASTEXITCODE
if ($code -ge 8) {
    Write-Error "Sync failed (robocopy exit code $code)"
    exit $code
}

# 重新生成导航
Push-Location $PSScriptRoot
try {
    python (Join-Path $PSScriptRoot "gen_zensical_config.py")
    if ($LASTEXITCODE -ne 0) {
        Write-Error "nav generation failed"
        exit $LASTEXITCODE
    }

    # 重新构建
    python -m zensical build --clean
    if ($LASTEXITCODE -ne 0) {
        Write-Error "build failed"
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}

Write-Host "Sync done." -ForegroundColor Green