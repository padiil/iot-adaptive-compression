import csv
import grpc
import os
import signal
import sys
import time
import zlib
from concurrent import futures

import lz4.frame

from proto import DataTransferServicer, add_DataTransferServicer_to_server, ServerResponse
from database import Database
from utils import setup_logger

logger = setup_logger()

CSV_FILE = "/app/data/analisis_latensi.csv"


class DataTransferService(DataTransferServicer):
    """gRPC service that logs to CSV and MongoDB"""

    def __init__(self, db: Database):
        self.db = db
        self.received_count = 0

        # Buat folder data jika belum ada
        os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
        
        # Reset file CSV setiap kali server nyala (Mode 'w')
        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "timestamp_kirim",
                "timestamp_terima",
                "latensi_ms",
                "tipe_kompresi",
                "ukuran_paket_bytes",
                "ukuran_asli_bytes",
                "hemat_persen",
                "waktu_proses_server_ms",
            ])

    def SendStream(self, request_iterator, context):
        logger.info("🔌 Client terhubung! Stream dimulai...")
        success_count = 0

        try:
            for sensor_data in request_iterator:
                start_process = time.time()
                self.received_count += 1

                # --- 1. LOGIKA DEKOMPRESI ---
                try:
                    if sensor_data.compression_type == "GZIP":
                        payload_asli = zlib.decompress(sensor_data.data)
                    elif sensor_data.compression_type == "LZ4":
                        # Menggunakan Frame Decompression (Standar)
                        payload_asli = lz4.frame.decompress(sensor_data.data)
                    else:
                        # RAW
                        payload_asli = sensor_data.data
                except Exception as exc:
                    # Log error tapi jangan matikan server, lanjut ke data berikutnya
                    logger.error(f"❌ Gagal dekompresi {sensor_data.compression_type}: {exc}")
                    continue

                # --- 2. HITUNG METRIK ---
                waktu_terima = time.time()
                latensi_ms = (waktu_terima - sensor_data.timestamp) * 1000

                uk_asli = len(payload_asli)
                uk_paket = len(sensor_data.data)
                
                hemat_persen = 0.0
                if uk_asli > 0:
                    hemat_persen = 100 - (uk_paket / uk_asli * 100)

                proc_ms = (time.time() - start_process) * 1000

                # --- 3. TULIS KE CSV (Laporan) ---
                with open(CSV_FILE, "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        f"{sensor_data.timestamp:.4f}",
                        f"{waktu_terima:.4f}",
                        f"{latensi_ms:.2f}",
                        sensor_data.compression_type,
                        uk_paket,
                        uk_asli,
                        f"{hemat_persen:.1f}",
                        f"{proc_ms:.3f}",
                    ])

                # --- 4. TULIS KE MONGODB (Sistem) ---
                doc = {
                    "sensor_id": sensor_data.sensor_id,
                    "timestamp_kirim": sensor_data.timestamp, # Nanti dikonversi jadi Date di db_handler
                    "timestamp_terima": waktu_terima,
                    "latensi_ms": latensi_ms,
                    "compression_type": sensor_data.compression_type,
                    "data_size": uk_paket,
                    # Simpan data mentah (binary)
                    "raw_data": sensor_data.data, 
                }

                if self.db.insert_sensor_data(doc):
                    success_count += 1

                # Log periodic (biar terminal gak penuh spam)
                if self.received_count % 50 == 0:
                    logger.info(
                        f"📊 Paket #{self.received_count} | {sensor_data.compression_type:4s} | Latensi: {latensi_ms:.1f}ms | Hemat: {hemat_persen:.1f}%"
                    )

        except Exception as exc:
            logger.error(f"❌ Error Stream: {exc}")
            return ServerResponse(success=False, message=str(exc))

        return ServerResponse(success=True, message=f"Selesai. Total: {success_count}")


def serve():
    db = Database()
    try:
        db.connect()
    except Exception as exc:
        logger.error(f"❌ DB Error: {exc}")
        sys.exit(1)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_DataTransferServicer_to_server(DataTransferService(db), server)

    port = os.getenv("GRPC_PORT", "50051")
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info(f"🚀 Central Node (MongoDB + CSV) running on port {port}")

    def signal_handler(sig, frame):
        logger.info("🛑 Menerima signal shutdown...")
        server.stop(5)
        db.close()
        logger.info("✅ Server dihentikan dengan aman")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    logger.info("=" * 40)
    logger.info("🏢 CENTRAL NODE - IoT Analysis Server")
    logger.info("=" * 40)
    serve()