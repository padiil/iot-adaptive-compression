# Demo Script: Trigger GZIP Mode (Critical Network Simulation)
Write-Host "DEMO: Simulating Critical Network Congestion (GZIP Mode)" -ForegroundColor Red
Write-Host "================================================" -ForegroundColor Red
Write-Host ""
Write-Host "What we are doing:" -ForegroundColor Yellow
Write-Host "   - Add 100ms network delay + 10% packet loss"
Write-Host "   - Queue will fill up to 700-999 range"
Write-Host "   - System switches to GZIP (maximum compression)"
Write-Host ""

Write-Host "Installing traffic control tools (if not installed)..." -ForegroundColor Green
docker exec iot-edge-node apk add --no-cache iproute2 2>$null

Write-Host "Adding SEVERE network delay (100ms + 10% loss)..." -ForegroundColor Red
docker exec iot-edge-node tc qdisc del dev eth0 root 2>$null
docker exec iot-edge-node tc qdisc add dev eth0 root netem delay 100ms loss 10%

Write-Host ""
Write-Host "Expected behavior:" -ForegroundColor Yellow
Write-Host "   - Severe delay causes massive queue buildup"
Write-Host "   - Queue: 700-999"
Write-Host "   - Mode switches: RAW to LZ4 to GZIP"
Write-Host "   - Compression: ~96% (2720 to 105 bytes!)"
Write-Host ""

Start-Sleep -Seconds 3

Write-Host "Monitoring logs for GZIP activation..." -ForegroundColor Red
Write-Host "   Look for: level=WARN msg=`"Jaringan Macet`" mode=GZIP" -ForegroundColor Cyan
Write-Host "   Notice: saved_pct=96%" -ForegroundColor Yellow
Write-Host "   Press Ctrl+C to stop"
Write-Host ""

docker compose logs -f edge-node
