#!/bin/bash
# Demo Script: Trigger LZ4 Mode (Moderate Congestion)

echo "🎬 DEMO: Simulating Network Congestion (LZ4 Mode)"
echo "================================================"
echo ""
echo "📝 What we're doing:"
echo "   - Temporarily increase data generation rate"
echo "   - Queue will build up to 300-700 range"
echo "   - System switches to LZ4 compression"
echo ""

# Backup original file
docker exec iot-edge-node cp /root/services/sensor.go /root/services/sensor.go.backup

# Reduce sleep time to 8ms (faster generation)
docker exec iot-edge-node sh -c "sed -i 's/time.Sleep(20/time.Sleep(8/' /root/services/sensor.go"

echo "⚙️  Modified data generation rate: 20ms → 8ms"
echo "📊 Expected queue buildup: 300-500"
echo ""
echo "🔄 Restarting edge node..."
docker compose restart edge-node

echo ""
echo "✅ Now monitoring logs for LZ4 mode activation..."
echo "   Press Ctrl+C when you see 'mode=LZ4'"
echo ""

sleep 3
docker compose logs -f edge-node
