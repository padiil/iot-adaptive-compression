package models

type LocalData struct {
	SensorID string
	Temp     float32
	Time     float64
	Payload  []byte
}
