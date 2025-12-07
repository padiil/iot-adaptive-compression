Write-Host "Database Verification" -ForegroundColor Magenta
Write-Host "================================================" -ForegroundColor Magenta
Write-Host ""

Write-Host "Total records in database..." -ForegroundColor Yellow
docker exec iot-postgres psql -U postgres -d iot_data -c "SELECT COUNT(*) as total_records FROM sensor_data;"

Write-Host ""
Write-Host "Compression type distribution:" -ForegroundColor Yellow
docker exec iot-postgres psql -U postgres -d iot_data -c "SELECT compression_type, COUNT(*) as count, ROUND(AVG(LENGTH(data))) as avg_size_bytes FROM sensor_data GROUP BY compression_type ORDER BY compression_type;"

Write-Host ""
Write-Host "Recent 10 records:" -ForegroundColor Yellow
docker exec iot-postgres psql -U postgres -d iot_data -c "SELECT sensor_id, TO_TIMESTAMP(timestamp) as time, compression_type, LENGTH(data) as size_bytes FROM sensor_data ORDER BY timestamp DESC LIMIT 10;"

Write-Host ""
Write-Host "Statistics Summary:" -ForegroundColor Cyan
docker exec iot-postgres psql -U postgres -d iot_data -c "SELECT compression_type, COUNT(*) as records, MIN(LENGTH(data)) as min_bytes, MAX(LENGTH(data)) as max_bytes, AVG(LENGTH(data))::int as avg_bytes FROM sensor_data GROUP BY compression_type ORDER BY compression_type;"

Write-Host ""
Write-Host "Database verification complete!" -ForegroundColor Green
