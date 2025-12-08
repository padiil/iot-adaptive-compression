import os
import logging
from pymongo import MongoClient
from datetime import datetime

logger = logging.getLogger("central-node")

class Database:
    """MongoDB database handler"""

    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        
        # Config
        self.host = os.getenv("DB_HOST", "mongodb")
        self.port = int(os.getenv("DB_PORT", "27017"))
        self.db_name = os.getenv("DB_NAME", "iot_data")
        self.col_name = "sensor_stream"

    def connect(self):
        """Connect to MongoDB and prepare Time Series collection"""
        try:
            self.client = MongoClient(host=self.host, port=self.port)
            self.db = self.client[self.db_name]
            
            # Cek apakah collection sudah ada
            curr_colls = self.db.list_collection_names()
            
            if self.col_name not in curr_colls:
                # Buat Baru sebagai Time Series
                try:
                    self.db.create_collection(
                        self.col_name,
                        timeseries={
                            "timeField": "timestamp_kirim", # Field penentu waktu
                            "metaField": "sensor_id",       # Field metadata
                            "granularity": "seconds"        # Data masuk tiap detik
                        }
                    )
                    logger.info(f"✨ Membuat Time Series Collection: {self.col_name}")
                except Exception as e:
                    logger.warning(f"Info create collection: {e}")
            
            self.collection = self.db[self.col_name]

            # Ping cek koneksi
            self.client.admin.command("ping")
            logger.info(f"✅ Terhubung ke MongoDB: {self.host}:{self.port}/{self.db_name}")

        except Exception as exc:
            logger.error(f"❌ Gagal koneksi MongoDB: {exc}")
            raise

    def insert_sensor_data(self, data_dict: dict) -> bool:
        """Insert data"""
        try:
            # Data dari gRPC masih float (unix timestamp), harus di-convert
            if isinstance(data_dict.get("timestamp_kirim"), float):
                data_dict["timestamp_kirim"] = datetime.fromtimestamp(data_dict["timestamp_kirim"])
            
            # Tambah created_at server
            data_dict["created_at"] = datetime.utcnow()
            
            self.collection.insert_one(data_dict)
            return True
        except Exception as exc:
            logger.error(f"❌ Gagal insert Mongo: {exc}")
            return False

    def close(self):
        if self.client:
            self.client.close()
            logger.info("🔌 Koneksi MongoDB ditutup")