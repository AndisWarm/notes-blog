# Sync study notes into this site's docs directory.
# Usage: powershell -ExecutionPolicy Bypass -File sync.ps1
$ErrorActionPreference = "Stop"

$src = "F:\知识库\豆瓣读书\学习笔记"
$dst = Join-Path $PSScriptRoot "docs"

if (-not (Test-Path $src)) {
    Write-Error "Source directory not found: $src"
    exit 1
}

# /MIR mirrors the source (removes extra files in dst).
# /XD excludes node_modules and .git; /XF excludes temp files.
robocopy $src $dst /MIR /XD node_modules .git /XF *.tmp *.temp *.log /NFL /NDL /NJH /NP

$code = $LASTEXITCODE
if ($code -lt 8) {
    Write-Host "Sync done (robocopy exit code $code, 0-7 is OK)" -ForegroundColor Green
    exit 0
} else {
    Write-Error "Sync failed (robocopy exit code $code)"
    exit $code
}