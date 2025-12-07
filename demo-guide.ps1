Write-Host '================================================' -ForegroundColor Cyan
Write-Host '  IoT Adaptive Compression - Demo Guide' -ForegroundColor Cyan
Write-Host '================================================' -ForegroundColor Cyan
Write-Host ''

Write-Host 'MENU DEMONSTRASI:' -ForegroundColor Yellow
Write-Host ''
Write-Host '1. Mode NORMAL (RAW)' -ForegroundColor Green
Write-Host '   - Jaringan lancar, no compression'
Write-Host '   - Queue: 0-10, Latency: ~250ns'
Write-Host '   - Command: docker compose up -d'
Write-Host ''

Write-Host '2. Mode CONGESTED (LZ4)' -ForegroundColor Yellow
Write-Host '   - Jaringan padat, fast compression'
Write-Host '   - Queue: 300-700, Compression: ~85%, Latency: ~5-10us'
Write-Host '   - Command: .\demo-congestion.ps1'
Write-Host ''

Write-Host '3. Mode CRITICAL (GZIP)' -ForegroundColor Red
Write-Host '   - Jaringan macet, maximum compression'
Write-Host '   - Queue: 700-999, Compression: ~96%, Latency: ~100us'
Write-Host '   - Command: .\demo-critical.ps1'
Write-Host ''

Write-Host '4. Reset to Normal' -ForegroundColor Cyan
Write-Host '   - Command: .\demo-reset.ps1'
Write-Host ''

Write-Host '5. Check Database' -ForegroundColor Magenta
Write-Host '   - Command: .\demo-database.ps1'
Write-Host ''

Write-Host '================================================' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Quick Start: docker compose up -d' -ForegroundColor Green
Write-Host ''
