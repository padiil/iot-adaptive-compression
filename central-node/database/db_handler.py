import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional
import logging

logger = logging.getLogger("central-node")


class Database:
    """PostgreSQL database handler"""

    def __init__(self):
        self.conn: Optional[psycopg2.extensions.connection] = None
        self.host = os.getenv("DB_HOST", "postgres")
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "iot_data")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "postgres")

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info(
                f"✅ Terhubung ke database PostgreSQL: {self.host}:{self.port}/{self.database}")
            self._create_tables()
        except Exception as e:
            logger.error(f"❌ Gagal koneksi ke database: {e}")
            raise

    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            cursor = self.conn.cursor()

            # Create sensor_data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id SERIAL PRIMARY KEY,
                    sensor_id VARCHAR(50) NOT NULL,
                    timestamp DOUBLE PRECISION NOT NULL,
                    compression_type VARCHAR(20) NOT NULL,
                    data_size INTEGER NOT NULL,
                    data BYTEA NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sensor_timestamp 
                ON sensor_data(sensor_id, timestamp)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_compression_type 
                ON sensor_data(compression_type)
            """)

            self.conn.commit()
            cursor.close()
            logger.info("✅ Tabel database siap")
        except Exception as e:
            logger.error(f"❌ Gagal membuat tabel: {e}")
            raise

    def insert_sensor_data(self, sensor_id: str, timestamp: float,
                           compression_type: str, data: bytes) -> bool:
        """Insert sensor data into database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO sensor_data (sensor_id, timestamp, compression_type, data_size, data)
                VALUES (%s, %s, %s, %s, %s)
            """, (sensor_id, timestamp, compression_type, len(data), data))

            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"❌ Gagal insert data: {e}")
            self.conn.rollback()
            return False

    def get_stats(self):
        """Get statistics from database"""
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT 
                    compression_type,
                    COUNT(*) as count,
                    AVG(data_size) as avg_size,
                    SUM(data_size) as total_size
                FROM sensor_data
                GROUP BY compression_type
            """)

            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"❌ Gagal get stats: {e}")
            return []

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("🔌 Koneksi database ditutup")
