# Link the plugin source into a local VAM/VaMX install for development.
# Usage:
#   .\scripts\install-dev.ps1
#   .\scripts\install-dev.ps1 -VamRoot "E:\VaMX"

param(
    [string]$VamRoot = $env:VAM_ROOT
)

$ErrorActionPreference = "Stop"

if (-not $VamRoot) {
    $VamRoot = "E:\VaMX"
}

$VamRoot = [System.IO.Path]::GetFullPath($VamRoot)
$exe = Join-Path $VamRoot "VaM.exe"
if (-not (Test-Path $exe)) {
    throw "VaM.exe not found in $VamRoot. Pass -VamRoot or set VAM_ROOT."
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$src = Join-Path $repoRoot "plugin"
$destParent = Join-Path $VamRoot "Custom\Scripts\VamMcp"
$dest = Join-Path $destParent "Bridge"

New-Item -ItemType Directory -Force -Path $destParent | Out-Null

if (Test-Path $dest) {
    $item = Get-Item $dest -Force
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        cmd /c rmdir "$dest"
    }
    else {
        Remove-Item $dest -Recurse -Force
    }
}

cmd /c mklink /J "$dest" "$src" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Junction failed; copying files instead."
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Copy-Item (Join-Path $src "VamMcpBridge.cs") (Join-Path $dest "VamMcpBridge.cs") -Force
    Copy-Item (Join-Path $src "meta.json") (Join-Path $dest "meta.json") -Force
}

Write-Host "Plugin available at: $dest\VamMcpBridge.cs"
Write-Host "In VAM: Main UI -> Session Plugins -> Add Plugin -> that file."
Write-Host "Then Session Plugin Presets -> set current as user default."
