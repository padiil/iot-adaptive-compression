package main

import (
	"context"
	"log"
	"time"

	"log/slog"
	"os"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	"edge-node/config"
	"edge-node/models"
	pb "edge-node/proto"
	"edge-node/services"
	"edge-node/utils"
)

func main() {
	// 1. Inisialisasi Koneksi
	logger := slog.New(slog.NewTextHandler(os.Stdout, nil))
	slog.SetDefault(logger)

	slog.Info("Menghubungkan ke Central Node", "address", config.ServerAddress)
	conn, err := grpc.Dial(config.ServerAddress, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("Gagal konek ke server: %v", err)
	}
	defer conn.Close()

	client := pb.NewDataTransferClient(conn)
	stream, err := client.SendStream(context.Background())
	if err != nil {
		slog.Error("Gagal konek ke server", "error", err)
		os.Exit(1)
	}

	slog.Info("Stream Terbuka! Sistem berjalan...")

	// 2. Setup Antrian & Sensor
	dataQueue := make(chan models.LocalData, config.QueueCap)
	go services.GenerateDummyData(dataQueue)

	// 3. Loop Utama
	for {
		data := <-dataQueue
		currentQueueSize := len(dataQueue)

		var finalPayload []byte
		var compType string

		startProcess := time.Now()

		// --- LOGIKA ADAPTIF ---
		if currentQueueSize > config.ThresholdHigh {
			compType = "GZIP"
			finalPayload = utils.CompressGzip(data.Payload)
		} else if currentQueueSize > config.ThresholdMedium {
			compType = "LZ4"
			finalPayload = utils.CompressLz4(data.Payload)
		} else {
			compType = "RAW"
			finalPayload = data.Payload
		}

		processingTime := time.Since(startProcess)

		// Logging & Kirim
		utils.PrintStatus(currentQueueSize, compType, len(data.Payload), len(finalPayload), processingTime)

		req := &pb.SensorData{
			SensorId:        data.SensorID,
			Timestamp:       data.Time,
			CompressionType: compType,
			Data:            finalPayload,
		}

		if err := stream.Send(req); err != nil {
			slog.Error("Error kirim data", "error", err)
			break
		}

		time.Sleep(20 * time.Millisecond)
	}

	// Cleanup
	resp, err := stream.CloseAndRecv()
	if err != nil {
		slog.Error("Error close stream", "error", err)
	}
	slog.Info("Server Response", "message", resp.GetMessage())
}
