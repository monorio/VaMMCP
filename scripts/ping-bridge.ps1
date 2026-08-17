# Write a ping command and wait for the session plugin to answer.
param(
    [string]$VamRoot = $env:VAM_ROOT
)

$ErrorActionPreference = "Stop"
if (-not $VamRoot) { $VamRoot = "E:\VaMX" }

$bridge = Join-Path $VamRoot "Saves\PluginData\vam-mcp"
if (-not (Test-Path $bridge)) {
    throw "Bridge folder missing: $bridge  (start VAM and load VamMcpBridge)"
}

$id = [guid]::NewGuid().ToString("N")
$command = @{ id = $id; op = "ping" } | ConvertTo-Json -Compress
$cmdPath = Join-Path $bridge "command.json"
$resPath = Join-Path $bridge "result.json"
if (Test-Path $resPath) { Remove-Item $resPath -Force }
# Windows PowerShell 5 Set-Content -Encoding UTF8 writes a BOM;
# SimpleJSON in VAM may reject that file.
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($cmdPath, $command, $utf8NoBom)

$deadline = (Get-Date).AddSeconds(10)
while ((Get-Date) -lt $deadline) {
    if (Test-Path $resPath) {
        $text = Get-Content $resPath -Raw
        if ($text -match $id) {
            Write-Host $text
            exit 0
        }
    }
    Start-Sleep -Milliseconds 100
}

throw "No plugin response. Is VamMcpBridge loaded as a Session Plugin?"
