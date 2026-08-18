# Build VamMcp.Bridge.N.var for GitHub Releases.
# Usage: .\scripts\pack-var.ps1
#        .\scripts\pack-var.ps1 -Version 1

param(
    [int]$Version = 1
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pluginDir = Join-Path $repoRoot "plugin"
$cs = Join-Path $pluginDir "VamMcpBridge.cs"
$metaSrc = Join-Path $pluginDir "meta.json"
if (-not (Test-Path $cs)) { throw "Missing $cs" }
if (-not (Test-Path $metaSrc)) { throw "Missing $metaSrc" }

$outDir = Join-Path $repoRoot "dist-var"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$stage = Join-Path $outDir "stage"
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
$scriptDest = Join-Path $stage "Custom\Scripts\VamMcp\Bridge"
New-Item -ItemType Directory -Force -Path $scriptDest | Out-Null
Copy-Item $cs (Join-Path $scriptDest "VamMcpBridge.cs")
Copy-Item $metaSrc (Join-Path $stage "meta.json")

$varName = "VamMcp.Bridge.$Version.var"
$varPath = Join-Path $outDir $varName
if (Test-Path $varPath) { Remove-Item $varPath -Force }

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($stage, $varPath)

Remove-Item $stage -Recurse -Force
Write-Host "Wrote $varPath"
Write-Host "Release artifact only. For normal installation, run scripts\install-dev.ps1 so the plugin is available under VAM_ROOT\Custom\Scripts."
