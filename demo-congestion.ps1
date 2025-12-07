# Demo Script: Trigger LZ4 Mode (Network Simulation)
Write-Host "DEMO: Simulating Network Congestion (LZ4 Mode)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "What we are doing:" -ForegroundColor Yellow
Write-Host "   - Add 50ms network delay using tc (traffic control)"
Write-Host "   - Queue will build up to 300-700 range"
Write-Host "   - System switches to LZ4 compression"
Write-Host ""

Write-Host "Installing traffic control tools..." -ForegroundColor Green
docker exec iot-edge-node apk add --no-cache iproute2 2>$null

Write-Host "Adding 50ms network delay..." -ForegroundColor Yellow
docker exec iot-edge-node tc qdisc add dev eth0 root netem delay 50ms

Write-Host ""
Write-Host "Expected behavior:" -ForegroundColor Yellow
Write-Host "   - Network delay causes queue buildup"
Write-Host "   - Queue: 300-700"
Write-Host "   - Mode switches: RAW to LZ4"
Write-Host "   - Compression: ~96% (LZ4 is VERY efficient)"
Write-Host ""

Start-Sleep -Seconds 3

Write-Host "Monitoring logs for LZ4 activation..." -ForegroundColor Green
Write-Host "   Look for: level=WARN msg=`"Jaringan Padat`" mode=LZ4" -ForegroundColor Cyan
Write-Host "   Press Ctrl+C to stop"
Write-Host ""

docker compose logs -f edge-node
