import os
import time
import pandas as pd
import streamlit as st
import plotly.express as px
import requests
from pymongo import MongoClient

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="IoT Command Center",
    page_icon="📡",
    layout="wide",
)

# --- 2. KONEKSI MONGODB ---
@st.cache_resource
def init_connection():
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
    return MongoClient(MONGO_URI)

client = init_connection()
db = client[os.getenv("DB_NAME", "iot_data")]
collection = db[os.getenv("COLLECTION_NAME", "sensor_stream")]

def send_command(case_id: int):
    try:
        url = f"http://edge-node:8080/case/{case_id}"
        requests.get(url, timeout=1)
    except Exception:
        pass

# Warna Grafik Konsisten
COLOR_MAP = {
    "RAW": "#00CC96",  # Hijau
    "LZ4": "#FFA15A",  # Oranye
    "GZIP": "#EF553B"  # Merah
}

# --- 3. LOGIKA UTAMA ---
def main():
    # --- A. SIDEBAR ---
    with st.sidebar:
        st.header("🎛️ Kendali Simulasi")
        
        if st.button("1️⃣ Normal (RAW)", use_container_width=True, key="btn_raw"):
            send_command(1)
            st.toast("✅ Mode: Normal", icon="🟢")
            
        st.write("")
        if st.button("2️⃣ Padat (LZ4)", use_container_width=True, key="btn_lz4"):
            send_command(2)
            st.toast("✅ Mode: Padat", icon="🟠")
            
        st.write("")
        if st.button("3️⃣ Sinyal Buruk (LZ4)", use_container_width=True, key="btn_bad"):
            send_command(3)
            st.toast("✅ Mode: Sinyal Buruk", icon="🟠")

        st.write("")
        if st.button("4️⃣ KRITIS (GZIP)", use_container_width=True, key="btn_gzip"):
            send_command(4)
            st.toast("✅ Mode: KRITIS!", icon="🔥")

        st.divider()
        st.info(f"🕒 Update: {time.strftime('%H:%M:%S')}")

    # --- B. JUDUL ---
    st.title("📡 Real-time IoT Compression Analysis")
    
    # Placeholder Besar
    dashboard_placeholder = st.empty()

    with dashboard_placeholder.container():
        # --- AMBIL DATA ---
        cursor = collection.find().sort("timestamp_kirim", -1).limit(100)
        data = list(cursor)

        if not data:
            st.warning("⏳ Menunggu data dari Edge Node...")
            time.sleep(2)
            st.rerun()
            return

        df = pd.DataFrame(data)

        # Preprocessing
        if "timestamp_kirim" in df.columns:
            df["timestamp_kirim"] = pd.to_datetime(df["timestamp_kirim"])
        df = df.sort_values(by="timestamp_kirim")

        # Fix Data Size
        if "raw_data" not in df.columns: df["raw_data"] = b""
        if "data_size" not in df.columns: df["data_size"] = df["raw_data"].apply(len)
        
        # Logika Estimasi Ukuran Asli
        if "original_size" not in df.columns:
            df["original_size"] = df["data_size"]
        
        mask_fix = (df["compression_type"] == "GZIP") & (df["original_size"] <= df["data_size"])
        df.loc[mask_fix, "original_size"] = 2720

        # Data Terakhir
        latest = df.iloc[-1]
        mode = latest.get("compression_type", "RAW")
        latency = latest.get("latensi_ms", 0.0)
        
        orig = latest.get("original_size", 2720)
        net = latest.get("data_size", 2720)
        saving = 100 - (net / orig * 100) if orig > 0 else 0

        # Smoothing Latensi
        if "latensi_ms" in df.columns:
            df["latensi_smooth"] = df["latensi_ms"].rolling(window=5, min_periods=1).mean()
        else:
            df["latensi_smooth"] = 0

        # --- RENDER KPI ---
        kpi_cols = st.columns(4)
        kpi_cols[0].metric("Total Paket", f"{collection.count_documents({})}")
        
        if mode == "GZIP":
            kpi_cols[1].error(f"🔥 Mode: {mode}")
        elif mode == "LZ4":
            kpi_cols[1].warning(f"⚠️ Mode: {mode}")
        else:
            kpi_cols[1].success(f"✅ Mode: {mode}")

        kpi_cols[2].metric("Latensi", f"{latency:.2f} ms")
        kpi_cols[3].metric("Hemat Bandwidth", f"{saving:.1f}%")

        st.divider()

        # --- RENDER GRAFIK (VERTIKAL / ATAS BAWAH) ---
        
        # 1. Grafik Latensi (Full Width)
        st.subheader("📉 Latensi (ms)")
        fig_lat = px.line(df, x="timestamp_kirim", y="latensi_smooth", 
                            color="compression_type", color_discrete_map=COLOR_MAP, markers=True)
        st.plotly_chart(fig_lat, use_container_width=True, key=f"lat_chart_{time.time()}")

        st.write("") # Jarak

        # 2. Grafik Ukuran Data (Full Width)
        st.subheader("📊 Ukuran Data (Bytes)")
        df_melt = df.melt(id_vars=["timestamp_kirim"], value_vars=["data_size", "original_size"], 
                            var_name="Tipe", value_name="Bytes")
        df_melt["Tipe"] = df_melt["Tipe"].replace({"data_size": "Network (Kirim)", "original_size": "Sensor (Asli)"})
        
        fig_bar = px.bar(df_melt, x="timestamp_kirim", y="Bytes", color="Tipe", 
                            barmode="group", color_discrete_sequence=["#EF553B", "#636EFA"])
        st.plotly_chart(fig_bar, use_container_width=True, key=f"bar_chart_{time.time()}")

    # --- AUTO REFRESH ---
    time.sleep(1)
    st.rerun()

if __name__ == "__main__":
    main()