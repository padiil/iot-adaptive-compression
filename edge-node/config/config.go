package config

import "os"
var (
	ServerAddress   = getEnv("SERVER_ADDRESS", "central-node:50051")
	QueueCap        = 1000
	ThresholdMedium = 20
	ThresholdHigh   = 80
)

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
