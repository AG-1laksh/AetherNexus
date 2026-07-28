Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   Starting Aether-Nexus Industrial Copilot & Backends  " -ForegroundColor White -BackgroundColor Blue
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Booting Document Pipeline (port 8000), GraphRAG (port 8010), and Vite (port 5173)..." -ForegroundColor Green

Set-Location -Path (Join-Path $PSScriptRoot "frontend")
npm run dev
