# Demo Script: Reset to Normal Mode
Write-Host "DEMO: Resetting to Normal Mode (RAW)" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Restore original configuration (20ms)
Write-Host "Restoring original data generation rate (20ms)..." -ForegroundColor Yellow
$content = Get-Content "edge-node/services/sensor.go" -Raw
$content = $content -replace 'time\.Sleep\(\d+ \* time\.Millisecond\)', 'time.Sleep(20 * time.Millisecond)'
$content | Set-Content "edge-node/services/sensor.go" -NoNewline

Write-Host ""
Write-Host "Rebuilding edge node..." -ForegroundColor Green
docker compose up -d --build edge-node

Start-Sleep -Seconds 5

Write-Host ""
Write-Host "System reset to normal mode" -ForegroundColor Green
Write-Host "   Queue should return to: 0-10"
Write-Host "   Mode should return to: RAW"
Write-Host ""

docker compose logs -f edge-node
