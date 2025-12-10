package config

import (
	"sync"
	"time"
)

const (
	ServerAddress = "central-node:50051"
	QueueCap      = 1000
	// Threshold disetel lebar biar LZ4 kelihatan lama
	ThresholdMedium = 10
	ThresholdHigh   = 800
)

// DynamicConfig menyimpan settingan yang bisa berubah
type DynamicConfig struct {
	sync.RWMutex // Kunci biar gak crash pas diakses barengan
	SensorSleep  time.Duration
	NetworkSleep time.Duration
}

// Inisialisasi Default (Kasus 1)
var Current = &DynamicConfig{
	SensorSleep:  100 * time.Millisecond,
	NetworkSleep: 10 * time.Millisecond,
}

// Fungsi Aman untuk Mengubah Nilai
func (c *DynamicConfig) SetValues(sensorMs, netMs int) {
	c.Lock()
	defer c.Unlock()
	c.SensorSleep = time.Duration(sensorMs) * time.Millisecond
	c.NetworkSleep = time.Duration(netMs) * time.Millisecond
}

// Fungsi Aman untuk Membaca Nilai
func (c *DynamicConfig) GetValues() (time.Duration, time.Duration) {
	c.RLock()
	defer c.RUnlock()
	return c.SensorSleep, c.NetworkSleep
}
