# Latency and Throughput Analysis in Distributed IoT Stream Processing
 ## with Dynamic Data Compression Implementation at Edge Nodes

 ---

 ## 1. Project Overview

 This project simulates a high-throughput distributed IoT system to analyze the trade-offs between **Latency** (speed) and **Throughput** (data volume) under varying network conditions.

 The core feature is an **Adaptive Edge Node** that monitors its internal transmission queue. Based on the network status (queue buildup), it dynamically switches between compression algorithms to optimize data delivery:

 * **🟢 Normal State (Low Latency):** When the network is stable, data is sent in **RAW** format to minimize CPU usage and latency.
 * **🟡 Traffic Congestion (Balanced):** When the queue starts to fill, it switches to **LZ4** compression for a balance between speed and size.
 * **🔴 Network Critical (High Throughput):** When the network is severely throttled, it switches to **GZIP** to maximize bandwidth saving, ensuring data delivery despite high CPU cost.

 ## 2. System Architecture & Tech Stack

 The system is built using a Polyglot Microservices architecture containerized with Docker.

 ### A. Edge Node (The Sender)
 * **Technology:** Go (Golang) v1.23
 * **Role:** Simulates high-frequency sensor data generation and implements the adaptive compression logic.
 * **Why Go?** Chosen for its superior concurrency handling (Goroutines/Channels) and performance in handling high-throughput streams with minimal CPU overhead.

### B. Central Node (The Receiver)
* **Technology:** Python 3.11 with gRPC & PostgreSQL
* **Role:** Acts as the Cloud/Data Center. It receives the stream, decompresses data based on the flag, and stores it in PostgreSQL database with performance metrics. ### C. Communication Layer
 * **Protocol:** gRPC (HTTP/2)
 * **Serialization:** Protocol Buffers (Protobuf)
 * **Why gRPC?** Enables efficient bi-directional binary streaming, which is critical for IoT telemetry.

 ### D. Infrastructure & Simulation
 * **Containerization:** Docker & Docker Compose.
 * **Network Chaos:** **Pumba** is used to inject artificial network delays (latency) and packet loss to simulate real-world "bad internet" conditions, triggering the adaptive logic.

### E. Visual Dashboard (Streamlit)
* **Technology:** Python + Streamlit
* **Role:** Real-time web dashboard for monitoring and controlling the demo
* **Features:**
  - Real-time latency and bandwidth efficiency charts
  - Sidebar control: switch scenarios (RAW, LZ4, GZIP) directly from the web
  - Live statistics: incoming data, active mode, bandwidth savings
* **Access:**
  - Start the system, then open your browser at: [http://localhost:8501](http://localhost:8501)
  - Use the sidebar buttons to change the demo mode instantly

 ## 3. Project Structure

```text
iot-adaptive-compression/
├── central-node/           # Python Server Implementation
│   ├── server.py          # Main gRPC server
│   ├── requirements.txt   # Python dependencies
│   ├── proto/             # Generated gRPC code for Python
│   ├── database/          # PostgreSQL handler
│   ├── utils/             # Logger utilities
│   └── Dockerfile         # Python container config
├── edge-node/              # Go Client Implementation
│   ├── config/             # Configuration constants
│   ├── models/             # Internal data structures
│   ├── proto/              # Generated gRPC code for Go
│   ├── services/           # Sensor simulation logic
│   ├── utils/              # Compression & Logging utilities
│   ├── main.go             # Main adaptive logic entry point
│   ├── go.mod              # Go module definition
│   └── Dockerfile          # Go container config
├── proto/                  # Shared Protocol Definitions
│   └── iot.proto           # The gRPC contract
├── compose.yaml            # Docker Compose orchestration
└── README.md               # Documentation
``` ## 4. Adaptive Logic Mechanism

 The Edge Node implements a feedback loop based on the `Queue Size` (buffer backlog).

 | Queue Size | Network Status | Compression Mode | Goal |
 | :--- | :--- | :--- | :--- |
 | ** ** | Excellent | **RAW** (No Compression) | Lowest Latency |
 | ** ** | Congested | **LZ4** (Fast Compression) | Balance CPU/Bandwidth |
 | ** ** | Critical | **GZIP** (High Compression) | Max Throughput / Survival |

 ## 5. How to Run the Project

 ### Prerequisites
 * Docker and Docker Compose installed on your machine.

### Step 1: Build and Start the System
Run the following command in the root directory. This will build the Go and Python images and start the network including PostgreSQL database.

```bash
docker compose up --build
``` *Observation:*
 * You will see logs from `central-node` indicating it is ready.
 * You will see logs from `edge-node` showing the current mode (initially **RAW**).

 ### Step 2: Monitor System Behavior & Dashboard

- To monitor edge node logs:
```bash
docker compose logs -f edge-node
```
- To access the visual dashboard:
```bash
# Make sure all services are built and running
# Then open in your browser:
http://localhost:8501
```

**Dashboard Features:**
- Latency (moving average) and data size (original vs compressed) charts
- Sidebar control: click buttons to switch demo scenarios (RAW, LZ4, GZIP)
- Command status notifications (toast)

### Step 3: Simulate Network Congestion (Optional Chaos Testing)

- **Manual method:**
  - You can still use the old demo scripts, or
  - **Just click the sidebar buttons on the dashboard** to change the demo mode in real time!

**What You'll See:**
* Queue builds up: `queue=350` → Mode switches to **LZ4**
* Queue continues growing: `queue=750` → Mode switches to **GZIP**
* Compression ratio: ~96% (2720 bytes → 105 bytes)
* CPU latency increases: ~100µs (vs 250ns in RAW mode)

When network recovers (queue drains), system automatically switches back to RAW mode.

 ### Step 4: Verify Data Persistence
 Check that data is being stored in PostgreSQL:

```bash
docker exec iot-postgres psql -U postgres -d iot_data -c "SELECT COUNT(*), compression_type FROM sensor_data GROUP BY compression_type;"
```

Expected output:
```
 count | compression_type 
-------+------------------
  1500 | RAW
   250 | LZ4
   180 | GZIP
```

### Step 5: Stop the System
```bash
docker compose down
```

 ## 6. Interactive Demonstration Guide

- Now, besides using demo scripts, you can:
  - **Directly control the demo mode from the web dashboard** (left sidebar)
  - See the charts update in real time according to the selected mode

### 🎬 **Demo 1: Normal Mode (RAW - No Compression)**
```powershell
docker compose up -d
docker compose logs -f edge-node
```
**Expected Output:**
```
level=INFO msg="Jaringan Lancar" queue=0 mode=RAW size_in=2720 latency_cpu=250ns
```
**Explanation:** Network is stable, no compression needed. Prioritizes **minimum latency**.

---

### 🎬 **Demo 2: Congested Network (LZ4 - Fast Compression)**
```powershell
.\demo-congestion.ps1
```
**What Happens:**
- Data generation increases (20ms → 8ms)
- Queue builds up: **300-700**
- System switches to **LZ4** compression
- Compression ratio: ~85% (2720 → ~400 bytes)
- CPU latency: ~5-10µs

**Expected Output:**
```
level=WARN msg="Jaringan Padat - Kompresi Ringan" queue=450 mode=LZ4 size_in=2720 size_out=420 saved_pct=84.5
```

---

### 🎬 **Demo 3: Critical Network (GZIP - Maximum Compression)**
```powershell
.\demo-critical.ps1
```
**What Happens:**
- Data generation at max speed (20ms → 2ms)
- Queue fills up: **700-999**
- System switches to **GZIP** compression
- Compression ratio: ~96% (2720 → 105 bytes!)
- CPU latency: ~100µs (trade-off for bandwidth saving)

**Expected Output:**
```
level=WARN msg="Jaringan Macet - Kompresi Berat" queue=999 mode=GZIP size_in=2720 size_out=105 saved_pct=96.13 latency_cpu=100µs
```

---

### 🎬 **Demo 4: Reset to Normal**
```powershell
.\demo-reset.ps1
```
Restores system to normal operation (RAW mode).

---

### 🎬 **Demo 5: Database Verification**
```powershell
.\demo-database.ps1
```
Shows data persistence and compression statistics in PostgreSQL.

---

### 📊 **Key Metrics to Observe**

| Metric | RAW Mode | LZ4 Mode | GZIP Mode |
|--------|----------|----------|-----------|
| **Queue Size** | 0-10 | 300-700 | 700-999 |
| **Data Size** | 2720 bytes | ~400 bytes | ~105 bytes |
| **Compression** | 0% | ~85% | ~96% |
| **CPU Latency** | 250 ns | 5-10 µs | 100 µs |
| **Trade-off** | Speed ✅ | Balanced | Bandwidth ✅ |

---

## 7. Development Notes (Local Run)

 If you want to run without Docker for debugging:

 1.  **Start Server:**
     ```bash
     cd central-node
     python server.py
     ```
 2.  **Start Edge Node:**
     ```bash
     cd edge-node
     go mod tidy
     go run main.go
     ```

 *Note: Running locally usually has near-zero latency, so the adaptive logic might stay in RAW mode unless you manually increase the sensor generation rate.*