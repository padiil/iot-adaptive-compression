package api

import (
	"edge-node/config"
	"fmt"
	"net/http"
)

func StartControlServer() {
	// --- KASUS 1: IDEAL (RAW) ---
	// Sensor lambat (100ms), Net cepat (10ms) -> Antrian Kosong
	http.HandleFunc("/case/1", func(w http.ResponseWriter, r *http.Request) {
		config.Current.SetValues(100, 10)
		msg := "✅ KASUS 1 (RAW): Data Lancar, Antrian Kosong"
		fmt.Println("\n" + msg)
		w.Write([]byte(msg))
	})

	// --- KASUS 2: OVERLOAD DATA (LZ4) ---
	// Sensor (40ms) vs Network (50ms).
	// Selisih cuma 10ms.
	// Artinya: Butuh 100 siklus (5 detik) buat nambah 1 antrian.
	// Butuh waktu lamaaaa banget buat nyampe 800 (GZIP).
	// Jadi LZ4 akan tampil lama.
	http.HandleFunc("/case/2", func(w http.ResponseWriter, r *http.Request) {
		config.Current.SetValues(40, 50)
		msg := "⚠️ KASUS 2 (Smooth LZ4): Data Lumayan Lancar, Antrian Sedikit Naik"
		fmt.Println("\n" + msg)
		w.Write([]byte(msg))
	})

	// --- KASUS 3: GANGGUAN SINYAL (LZ4) ---
	// Sensor (100ms) vs Network (120ms).
	// Ini lebih lambat lagi. LZ4 bakal awet banget.
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
