# 🎯 Panduan Demonstrasi Proyek
## IoT Adaptive Compression System (MongoDB Version)

---

## **Persiapan**

1.  **Jalankan Sistem:**
    ```bash
    docker compose up -d --build
    ```
2.  **Buka Monitoring Log:**
    Buka terminal baru dan jalankan:
    ```bash
    docker compose logs -f edge-node
    ```
    *(Terminal ini akan menampilkan perubahan mode secara real-time)*

---

## **Cara Melakukan Demo**

Kita menggunakan **`demo_controller.py`** sebagai remote control.

1.  **Install Dependency (di laptop):**
    ```bash
    pip install requests pymongo
    ```
2.  **Jalankan Controller:**
    ```bash
    python demo_controller.py
    ```

---

## **Skenario**

### **1. Mode Normal (RAW)**
* Pilih menu **1** di controller.
* **Log:** `Mode: RAW`
* **Penjelasan:** Antrian kosong, sistem mengirim data mentah untuk latensi terendah.

### **2. Mode Padat (LZ4)**
* Pilih menu **2** di controller.
* **Log:** `Mode: LZ4` (Tunggu beberapa detik, antrian akan naik > 10).
* **Penjelasan:** Data sensor meningkat. Sistem menyeimbangkan beban dengan kompresi cepat (LZ4).

### **3. Mode Kritis (GZIP)**
* Pilih menu **3** di controller.
* **Log:** `Mode: GZIP` (Antrian akan melonjak > 800).
* **Penjelasan:** Jaringan macet total + data banjir. Sistem beralih ke GZIP untuk mencegah data loss, menghemat bandwidth hingga 96%.

### **4. Bukti Data**
* Pilih menu **4** di controller.
* Program akan menarik data langsung dari **MongoDB** dan menampilkan jumlah data per tipe kompresi.

---

## **Hasil Analisis**

Setiap data yang diterima oleh Central Node akan dicatat secara otomatis ke file CSV `hasil_analisis/analisis_latensi.csv`.

**Penjelasan Kolom CSV:**

| Kolom                  | Deskripsi                                                                 |
|------------------------|--------------------------------------------------------------------------|
| `timestamp_kirim`      | Waktu (epoch) data dikirim dari edge node                                |
| `timestamp_terima`     | Waktu (epoch) data diterima di central node                              |
| `latensi_ms`           | Selisih waktu kirim-terima (latensi jaringan, dalam milidetik)            |
| `tipe_kompresi`        | Algoritma kompresi yang digunakan (RAW, LZ4, GZIP)                       |
| `ukuran_paket_bytes`   | Ukuran data yang dikirim (setelah kompresi, dalam byte)                   |
| `ukuran_asli_bytes`    | Ukuran data asli sebelum kompresi (dalam byte)                            |
| `hemat_persen`         | Persentase penghematan bandwidth akibat kompresi                          |
| `waktu_proses_server_ms` | Waktu proses dekompresi dan pencatatan di server (milidetik)             |

File ini dapat digunakan untuk analisis performa, membuat grafik, atau laporan demo.

Contoh baris CSV:
```
timestamp_kirim,timestamp_terima,latensi_ms,tipe_kompresi,ukuran_paket_bytes,ukuran_asli_bytes,hemat_persen,waktu_proses_server_ms
1702123456.1234,1702123456.2345,11.11,GZIP,105,2720,96.1,0.45
```