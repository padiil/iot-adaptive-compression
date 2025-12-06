package services

import (
	"bytes"
	"fmt"
	"math/rand"
	"time"

	"edge-node/models"
)

func GenerateDummyData(queue chan<- models.LocalData) {
	sensorID := "Edge-Node-01"

	for {
		// Buat data dummy ~2KB
		baseString := fmt.Sprintf(`{"id":"%s","temp":%.2f,"vibration":%.4f,"status":"OK"}`,
			sensorID, rand.Float32()*100, rand.Float32()*10)

		var buffer bytes.Buffer
		for i := 0; i < 40; i++ {
			buffer.WriteString(baseString)
			buffer.WriteString("\n")
		}

		newData := models.LocalData{
			SensorID: sensorID,
			Temp:     rand.Float32() * 100,
			Time:     float64(time.Now().UnixNano()) / 1e9,
			Payload:  buffer.Bytes(),
		}

		select {
		case queue <- newData:
		default:
		}

		time.Sleep(10 * time.Millisecond)
	}
}
