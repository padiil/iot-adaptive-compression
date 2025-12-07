import grpc
from concurrent import futures
import time
import signal
import sys
import os

from proto import DataTransferServicer, add_DataTransferServicer_to_server, SensorData, ServerResponse
from database import Database
from utils import setup_logger

# Setup logger
logger = setup_logger()


class DataTransferService(DataTransferServicer):
    """Implementation of gRPC DataTransfer service"""

    def __init__(self, db: Database):
        self.db = db
        self.received_count = 0
        self.last_log_time = time.time()
        self.log_interval = 5  # Log stats every 5 seconds

    def SendStream(self, request_iterator, context):
        """Handle streaming sensor data from edge nodes"""
        logger.info("🔌 Client terhubung! Stream dimulai...")

        success_count = 0
        failed_count = 0

        try:
            for sensor_data in request_iterator:
                # Log received data
                self.received_count += 1

                # Decompress and save to database
                success = self.db.insert_sensor_data(
                    sensor_id=sensor_data.sensor_id,
                    timestamp=sensor_data.timestamp,
                    compression_type=sensor_data.compression_type,
                    data=sensor_data.data
                )

                if success:
                    success_count += 1
                else:
                    failed_count += 1

                # Periodic logging
                current_time = time.time()
                if current_time - self.last_log_time >= self.log_interval:
                    logger.info(
                        f"📊 Total data diterima: {self.received_count}")
                    self.last_log_time = current_time

        except Exception as e:
            logger.error(f"❌ Error saat menerima stream: {e}")
            return ServerResponse(
                success=False,
                message=f"Error: {str(e)}"
            )
        finally:
            logger.info(
                f"🔌 Client terputus. Total diterima: {self.received_count} (berhasil: {success_count}, gagal: {failed_count})")

        # Return single response at the end
        return ServerResponse(
            success=True,
            message=f"Stream selesai. Diterima {success_count} data"
        )


def serve():
    """Start the gRPC server"""
    # Initialize database
    db = Database()
    try:
        db.connect()
    except Exception as e:
        logger.error(f"❌ Gagal inisialisasi database: {e}")
        sys.exit(1)

    # Create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_DataTransferServicer_to_server(DataTransferService(db), server)

    # Get port from environment or use default
    port = os.getenv("GRPC_PORT", "50051")
    server.add_insecure_port(f'[::]:{port}')

    # Start server
    server.start()
    logger.info(f"🚀 Central Node berjalan di port {port}")
    logger.info("⏳ Menunggu koneksi dari Edge Node...")

    # Graceful shutdown handler
    def signal_handler(sig, frame):
        logger.info("\n🛑 Menerima signal shutdown...")
        server.stop(5)
        db.close()
        logger.info("✅ Server dihentikan dengan aman")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Keep server running
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutdown dari keyboard...")
        server.stop(5)
        db.close()


if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("🏢 CENTRAL NODE - IoT Adaptive Compression System")
    logger.info("=" * 50)
    serve()
