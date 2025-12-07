# 🎯 Panduan Demonstrasi Proyek
## IoT Adaptive Compression System

---

## **Ringkasan Proyek**

Sistem ini mendemonstrasikan **adaptive compression** pada edge node IoT yang secara otomatis menyesuaikan algoritma kompresi berdasarkan kondisi jaringan real-time.

### **Trade-off Utama:**
- **Jaringan Lancar** → RAW (no compression) → **Latency Rendah** (~250ns)
- **Jaringan Padat** → LZ4 (fast compression) → **Balanced** (~5-10µs, compression ~85%)
- **Jaringan Macet** → GZIP (max compression) → **Bandwidth Efisien** (~100µs, compression ~96%)

---

## **Persiapan Demonstrasi**

### 1. Start Sistem
```powershell
docker compose up -d
```

### 2. Cek Status Container
```powershell
docker compose ps
```

Pastikan semua container running:
- ✅ `iot-postgres` (Database)
- ✅ `iot-central-node` (Python gRPC Server)
- ✅ `iot-edge-node` (Go Client dengan Adaptive Logic)

---

## **Skenario Demonstrasi**

### **📊 Demo 1: Mode Normal (RAW)**

**Kondisi:** Jaringan stabil, no congestion

```powershell
# Monitor edge node logs
docker compose logs -f edge-node
```

**Output yang diharapkan:**
```
level=INFO msg="Jaringan Lancar" queue=0 mode=RAW size_in=2720 latency_cpu=250ns
```

**Penjelasan:**
- **Queue = 0**: Tidak ada backlog, data terkirim cepat
- **Mode = RAW**: Tidak perlu kompresi, prioritas kecepatan
- **Latency = 250ns**: Overhead processing minimal
- **Size = 2720 bytes**: Data asli tanpa kompresi

**Key Point:** Saat jaringan lancar, sistem memilih **speed over compression**.

---

### **⚠️ Demo 2: Mode Congested (LZ4)**

**Kondisi:** Simulasi jaringan mulai padat

```powershell
# Jalankan script demonstrasi
.\demo-congestion.ps1
```

**Apa yang terjadi:**
1. Script meningkatkan kecepatan data generation (20ms → 8ms)
2. Queue mulai terisi: **300-700**
3. Sistem otomatis switch ke **LZ4** compression
4. Data dikompres ~85%

**Output yang diharapkan:**
```
level=WARN msg="Jaringan Padat - Kompresi Ringan" queue=450 mode=LZ4 
  size_in=2720 size_out=~400 saved_pct=85.3 latency_cpu=5µs
```

**Analisis:**
- **Compression Ratio**: 2720 → 400 bytes (~85% reduction)
- **CPU Latency**: Meningkat dari 250ns ke ~5-10µs (acceptable trade-off)
- **Benefit**: Mengurangi bandwidth usage tanpa overhead berlebihan

**Key Point:** LZ4 = **fast compression** untuk kondisi padat moderat.

---

### **🚨 Demo 3: Mode Critical (GZIP)**

**Kondisi:** Simulasi jaringan sangat macet

```powershell
.\demo-critical.ps1
```

**Apa yang terjadi:**
1. Script meningkatkan data generation ke maksimal (20ms → 2ms)
2. Queue penuh: **700-999**
3. Sistem switch ke **GZIP** (maximum compression)
4. Trade-off: CPU latency meningkat drastis

**Output yang diharapkan:**
```
level=WARN msg="Jaringan Macet - Kompresi Berat" queue=999 mode=GZIP 
  size_in=2720 size_out=105 saved_pct=96.13 latency_cpu=100µs
```

**Analisis:**
- **Compression Ratio**: 2720 → 105 bytes (**96% reduction!**)
- **CPU Latency**: Meningkat ke ~100µs (400x lebih lambat dari RAW)
- **Benefit**: Bandwidth saving maksimal, data tetap terkirim meski jaringan parah

**Key Point:** GZIP = **survival mode** saat bandwidth sangat terbatas.

---

### **🔄 Demo 4: Recovery (Reset to Normal)**

**Kondisi:** Simulasi jaringan kembali normal

```powershell
.\demo-reset.ps1
```

**Apa yang terjadi:**
1. Script mengembalikan data generation ke normal (20ms)
2. Queue mulai kosong
3. Sistem otomatis kembali ke **RAW** mode

**Output:**
```
level=INFO msg="Jaringan Lancar" queue=5 mode=RAW size_in=2720 latency_cpu=280ns
```

**Key Point:** Sistem **self-healing** - otomatis kembali optimal saat jaringan pulih.

---

### **💾 Demo 5: Verifikasi Database**

**Tujuan:** Membuktikan semua data tersimpan di PostgreSQL

```powershell
.\demo-database.ps1
```

**Output contoh:**
```
Total records in database...
 total_records 
---------------
         26545

Compression type distribution:
 compression_type | count | avg_size_bytes 
------------------+-------+----------------
 GZIP             | 11491 |            105
 LZ4              |   180 |             99
 RAW              | 14881 |           2716

Statistics Summary:
 compression_type | records | min_bytes | max_bytes | avg_bytes 
------------------+---------+-----------+-----------+-----------
 GZIP             |   11491 |       100 |       105 |       105
 LZ4              |     180 |        97 |        99 |        99
 RAW              |   14894 |      2680 |      2720 |      2716
```

**Analisis:**
- ✅ Data dari semua mode tersimpan dengan metadata kompresi
- ✅ Central node berhasil decompress dan persist ke database
- ✅ Sistem dapat melacak efektivitas setiap algoritma kompresi

---

## **📈 Metrik Perbandingan**

| Mode | Queue Size | Data Size | Compression | CPU Latency | Use Case |
|------|-----------|-----------|-------------|-------------|----------|
| **RAW** | 0-10 | 2720 bytes | 0% | ~250 ns | Jaringan lancar, prioritas speed |
| **LZ4** | 300-700 | ~400 bytes | ~85% | ~5-10 µs | Jaringan padat, balanced |
| **GZIP** | 700-999 | ~105 bytes | ~96% | ~100 µs | Jaringan macet, survival mode |

**Trade-off Formula:**
```
Compression ↑  =  Bandwidth ↓  +  CPU Latency ↑
```

---

## **🎓 Poin Presentasi Kunci**

### 1. **Problem Statement**
IoT devices di edge network sering menghadapi jaringan tidak stabil. Solusi tradisional:
- ❌ **Always compress**: Buang CPU saat jaringan lancar
- ❌ **Never compress**: Bandwidth habis saat jaringan macet

### 2. **Solution: Adaptive Compression**
Sistem monitoring **queue size** sebagai indikator kesehatan jaringan:
- Queue kosong → Network OK → No compression (low latency)
- Queue penuh → Network congested → Aggressive compression (save bandwidth)

### 3. **Tech Stack Highlights**
- **Go (Edge Node)**: High-performance concurrency (Goroutines)
- **Python (Central Node)**: Rapid development, rich ecosystem (gRPC, PostgreSQL)
- **gRPC**: Efficient binary streaming (HTTP/2)
- **Docker Compose**: Reproducible multi-service architecture

### 4. **Real-world Impact**
- **Bandwidth Saving**: Up to 96% reduction (2720 → 105 bytes)
- **Latency Trade-off**: Acceptable CPU overhead (~100µs) vs network delay (often > 100ms)
- **Adaptive**: Self-adjusts without manual intervention

---

## **🔧 Troubleshooting**

### Container tidak start:
```powershell
docker compose down
docker compose up -d --build
```

### Logs tidak muncul:
```powershell
docker compose logs --tail=50 edge-node
docker compose logs --tail=50 central-node
```

### Reset database:
```powershell
docker compose down -v  # Hapus volumes
docker compose up -d
```

---

## **📞 Quick Commands**

```powershell
# Start
docker compose up -d

# Monitor
docker compose logs -f edge-node

# Database check
.\demo-database.ps1

# Stop
docker compose down
```

---

## **✅ Checklist Demo**

- [ ] System up and running (all 3 containers)
- [ ] Demo 1: Normal mode (RAW) - queue=0
- [ ] Demo 2: Congested mode (LZ4) - queue=300-700
- [ ] Demo 3: Critical mode (GZIP) - queue=700-999
- [ ] Demo 4: Recovery (back to RAW)
- [ ] Demo 5: Database verification
- [ ] Explain trade-off: Latency vs Bandwidth
- [ ] Highlight adaptive self-healing behavior

---

**Durasi Estimasi:** 10-15 menit  
**Audience Level:** Technical (DevOps, Backend Engineers, IoT Developers)
