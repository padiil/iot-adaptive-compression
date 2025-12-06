package utils

import (
	"log/slog"
	"os"
	"time"
)

var Logger = slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
	Level: slog.LevelInfo,
	ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
		if a.Key == slog.TimeKey {
			return slog.Attr{}
		}
		return a
	},
}))

func PrintStatus(queueSize int, mode string, originalSize, compressedSize int, procTime time.Duration) {
	// Hitung rasio hemat
	ratio := 0.0
	if originalSize > 0 {
		ratio = 100.0 - (float64(compressedSize)/float64(originalSize))*100.0
	}

	// Tentukan Log Level & Pesan berdasarkan Mode
	switch mode {
	case "LZ4":
		Logger.Info("Jaringan Padat - Kompresi Ringan",
			slog.Int("queue", queueSize),
			slog.String("mode", mode),
			slog.Int("size_in", originalSize),
			slog.Int("size_out", compressedSize),
			slog.Float64("saved_pct", ratio),
			slog.Duration("latency_cpu", procTime),
		)
	case "GZIP":
		Logger.Warn("Jaringan Macet - Kompresi Berat",
			slog.Int("queue", queueSize),
			slog.String("mode", mode),
			slog.Int("size_in", originalSize),
			slog.Int("size_out", compressedSize),
			slog.Float64("saved_pct", ratio),
			slog.Duration("latency_cpu", procTime),
		)
	default: // RAW
		Logger.Info("Jaringan Lancar",
			slog.Int("queue", queueSize),
			slog.String("mode", mode),
			slog.Int("size_in", originalSize),
			slog.Duration("latency_cpu", procTime),
		)
	}
}
