#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-Uv {
    $command = Get-Command uv -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $candidateDirs = @(
        (Join-Path $env:USERPROFILE '.local\bin'),
        (Join-Path $env:LOCALAPPDATA 'Programs\uv')
    )

    foreach ($dir in $candidateDirs) {
        $candidate = Join-Path $dir 'uv.exe'
        if (Test-Path $candidate) {
            $env:Path = "$dir;$env:Path"
            return $candidate
        }
    }

    throw "uv.exe was not found. Restart PowerShell after installing uv, or add C:\Users\<you>\.local\bin to PATH."
}

$uv = Resolve-Uv
$root = $PSScriptRoot

Write-Host "Starting Registry service on port 10000..."
$registry = Start-Process -FilePath $uv -ArgumentList @('run', 'python', '-m', 'registry') -WorkingDirectory $root -NoNewWindow -PassThru
Start-Sleep -Seconds 2

Write-Host "Starting Tax Agent on port 10102..."
$tax = Start-Process -FilePath $uv -ArgumentList @('run', 'python', '-m', 'tax_agent') -WorkingDirectory $root -NoNewWindow -PassThru

Write-Host "Starting Compliance Agent on port 10103..."
$compliance = Start-Process -FilePath $uv -ArgumentList @('run', 'python', '-m', 'compliance_agent') -WorkingDirectory $root -NoNewWindow -PassThru
Start-Sleep -Seconds 3

Write-Host "Starting Law Agent on port 10101..."
$law = Start-Process -FilePath $uv -ArgumentList @('run', 'python', '-m', 'law_agent') -WorkingDirectory $root -NoNewWindow -PassThru
Start-Sleep -Seconds 3

Write-Host "Starting Customer Agent on port 10100..."
$customer = Start-Process -FilePath $uv -ArgumentList @('run', 'python', '-m', 'customer_agent') -WorkingDirectory $root -NoNewWindow -PassThru

Write-Host ""
Write-Host "All services started:"
Write-Host "  Registry:         http://localhost:10000"
Write-Host "  Customer Agent:   http://localhost:10100"
Write-Host "  Law Agent:        http://localhost:10101"
Write-Host "  Tax Agent:        http://localhost:10102"
Write-Host "  Compliance Agent: http://localhost:10103"
Write-Host ""
Write-Host "Run test_client.py to send a query:"
Write-Host "  uv run python test_client.py"
Write-Host ""
Write-Host "Press Ctrl+C to stop all services."

Wait-Process -Id $registry.Id, $tax.Id, $compliance.Id, $law.Id, $customer.Id
