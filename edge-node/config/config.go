package config

import (
	"sync"
	"time"
)

// Konstanta Statis
const (
	ServerAddress   = "central-node:50051"
	QueueCap        = 1000
	ThresholdMedium = 10
	ThresholdHigh   = 800
)

// Konfigurasi Dinamis (Bisa diubah lewat API)
type DynamicConfig struct {
	sync.RWMutex
	SensorSleep  time.Duration // Mengatur Volume Data (Makin kecil = Makin Banyak Data)
	NetworkSleep time.Duration // Mengatur Latensi Jaringan (Makin besar = Makin Macet)
}

// Default awal: KASUS 1 (Normal & Lancar)
var Current = &DynamicConfig{
	SensorSleep:  100 * time.Millisecond, // 10 data/detik (Santai)
	NetworkSleep: 10 * time.Millisecond,  // Kirim ngebut
}

// Setter Aman
func (c *DynamicConfig) SetValues(sensorMs, netMs int) {
	c.Lock()
	defer c.Unlock()
	c.SensorSleep = time.Duration(sensorMs) * time.Millisecond
	c.NetworkSleep = time.Duration(netMs) * time.Millisecond
}

// Getter Aman
func (c *DynamicConfig) GetValues() (time.Duration, time.Duration) {
	c.RLock()
	defer c.RUnlock()
	return c.SensorSleep, c.NetworkSleep
}
