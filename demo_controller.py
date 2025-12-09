import requests
import time
import os
import sys
from pymongo import MongoClient
from datetime import datetime

# KONFIGURASI
API_URL = "http://localhost:8080"
MONGO_URI = "mongodb://localhost:27018"
DB_NAME = "iot_data"
COL_NAME = "sensor_stream"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def set_case(case_id):
    try:
        url = f"{API_URL}/case/{case_id}"
        resp = requests.get(url)
        print(f"\nCOMMAND SENT: {resp.text}")
    except Exception as e:
        print(f"Error contacting Edge Node: {e}")

def check_db_stats():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        col = db[COL_NAME]
        
        pipeline = [
            {
                "$group": {
                    "_id": "$compression_type",
                    "count": {"$sum": 1},
                    "avg_size": {"$avg": "$data_size"}
                }
            }
        ]
        
        results = list(col.aggregate(pipeline))
        total = col.count_documents({})
        
        print(f"\nDATABASE STATS (MongoDB)")
        print(f"   Total Records: {total}")
        print("   ------------------------------------------------")
        print(f"   {'MODE':<10} | {'COUNT':<8} | {'AVG SIZE (Bytes)':<15}")
        print("   ------------------------------------------------")
        
        for r in results:
            mode = r['_id']
            count = r['count']
            avg = round(r['avg_size'], 1)
            print(f"   {mode:<10} | {count:<8} | {avg:<15}")
            
    except Exception as e:
        print(f"Error checking DB: {e}")

def main():
    while True:
        clear_screen()
        print("========================================")
        print("   IoT ADAPTIVE DEMO CONTROLLER")
        print("========================================")
        print("1.  Case 1: NORMAL (RAW Mode)")
        print("2.  Case 2: HEAVY LOAD (LZ4 Mode - Smooth)")
        print("3.  Case 4: CRITICAL (GZIP Mode)")
        print("4.  Check Database Stats (MongoDB)")
        print("5.  Exit")
        print("========================================")
        
        choice = input("Pilih Menu (1-5): ")
        
        if choice == '1':
            set_case(1)
        elif choice == '2':
            set_case(2)
        elif choice == '3':
            set_case(4)
        elif choice == '4':
            check_db_stats()
        elif choice == '5':
            print("Bye!")
            sys.exit()
            
        input("\nTekan Enter untuk kembali ke menu...")

if __name__ == "__main__":
    main()