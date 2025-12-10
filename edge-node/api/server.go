package api

import (
	"fmt"
	"net/http"

	"edge-node/config"
)

func StartControlServer() {
	// --- KASUS 1: IDEAL (RAW) ---
	// Sensor lambat (100ms), Net cepat (10ms) -> Antrian Kosong
	http.HandleFunc("/case/1", func(w http.ResponseWriter, r *http.Request) {
		config.Current.SetValues(100, 10)
		msg := "✅ KASUS 1 (RAW): Data Lancar, Antrian Kosong"
		fmt.Println("\n" + msg) // Print di terminal Edge Node
		w.Write([]byte(msg))    // Kirim balasan ke Dashboard
	})

	// --- KASUS 2: OVERLOAD DATA (LZ4) ---
	// Sensor (40ms) vs Network (50ms).
	// Selisih cuma 10ms. Antrian naik perlahan.
	http.HandleFunc("/case/2", func(w http.ResponseWriter, r *http.Request) {
		config.Current.SetValues(40, 50)
		msg := "⚠️ KASUS 2 (Smooth LZ4): Data Lumayan Lancar, Antrian Sedikit Naik"
		fmt.Println("\n" + msg)
		w.Write([]byte(msg))
	})

	// --- KASUS 3: GANGGUAN SINYAL (LZ4) ---
	// Sensor (100ms) vs Network (120ms).
	// Data lambat, tapi jaringan lebih lambat. Antrian naik perlahan.
	http.HandleFunc("/case/3", func(w http.ResponseWriter, r *http.Request) {
		config.Current.SetValues(100, 120)
		msg := "⚠️ KASUS 3 (Stable LZ4): Data Lambat, Antrian Meningkat"
		fmt.Println("\n" + msg)
		w.Write([]byte(msg))
	})

	// --- KASUS 4: BENCANA (GZIP) ---
	// Sensor Gila (5ms), Net Macet Parah (100ms).
	// Antrian langsung meledak ke 1000 dalam sekejap.
	http.HandleFunc("/case/4", func(w http.ResponseWriter, r *http.Request) {
		config.Current.SetValues(5, 100)
		msg := "🔥 KASUS 4 (GZIP): Data banyak, Antrian membludak"
		fmt.Println("\n" + msg)
		w.Write([]byte(msg))
	})

	fmt.Println("🎛️  Control API Ready on port 8080...")
	go http.ListenAndServe(":8080", nil)
}
