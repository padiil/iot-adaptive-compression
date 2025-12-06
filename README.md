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
 * **Technology:** Go (Golang) v1.21
 * **Role:** Simulates high-frequency sensor data generation and implements the adaptive compression logic.
 * **Why Go?** Chosen for its superior concurrency handling (Goroutines/Channels) and performance in handling high-throughput streams.

 ### B. Central Node (The Receiver)
 * **Technology:** -
 * **Role:** Acts as the Cloud/Data Center. It receives the stream, decompresses data based on the flag, and logs performance metrics (send time, receive time, latency) to CSV.

 ### C. Communication Layer
 * **Protocol:** gRPC (HTTP/2)
 * **Serialization:** Protocol Buffers (Protobuf)
 * **Why gRPC?** Enables efficient bi-directional binary streaming, which is critical for IoT telemetry.

 ### D. Infrastructure & Simulation
 * **Containerization:** Docker & Docker Compose.
 * **Network Chaos:** **Pumba** is used to inject artificial network delays (latency) and packet loss to simulate real-world "bad internet" conditions, triggering the adaptive logic.

 ## 3. Project Structure

 ```text
 iot-adaptive-compression/
 ├── central-node/           # Server Implementation
 │   ├── ---
 │   ├── Dockerfile          # container config
 │   └── ---
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
 ```

 ## 4. Adaptive Logic Mechanism

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
 Run the following command in the root directory. This will build the Go and Python images and start the network.

 ```bash
 docker compose up --build
 ```

 *Observation:*
 * You will see logs from `central-node` indicating it is ready.
 * You will see logs from `edge-node` showing the current mode (initially **RAW**).

 ### Step 2: Simulate Network Failure (Chaos Testing)
 To verify the adaptive logic, we need to simulate a slow network. Open a **new terminal** and run Pumba (configured in `compose.yaml`) or use Linux `tc` commands if running locally.

 If using the provided Pumba configuration in `compose.yaml`, it runs automatically on a schedule.
 * **Wait for ~30 seconds**: Pumba will inject a **500ms delay** to the Edge Node container.
 * **Check Logs**: You will see the Edge Node queue building up rapidly.
 * **Verify Adaptation**: The logs will switch from `✅ Mode: RAW` to `⚠️ Mode: LZ4`, and finally to `🔥 Mode: GZIP`.

 ### Step 3: Analyze Results
 The Central Node logs every received packet to a CSV file.
 1.  Stop the containers: `Ctrl+C` or `docker compose down`.
 2.  Locate the data: `central-node/data/analisis_latensi.csv` (mapped via volume).
 3.  Use this CSV to generate graphs for the final report.

 ## 6. Development Notes (Local Run)

 If you want to run without Docker for debugging:

 1.  **Start Server:**
     ```bash
     cd central-node
     ---
     ```
 2.  **Start Edge Node:**
     ```bash
     cd edge-node
     go mod tidy
     go run main.go
     ```

 *Note: Running locally usually has near-zero latency, so the adaptive logic might stay in RAW mode unless you manually increase the sensor generation rate.*