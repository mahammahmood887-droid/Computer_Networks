# Network Traffic Monitoring Platform
### Computer Networks Project — Step-by-Step Guide

---

## Project Structure

```
network_monitor/
│
├── app.py                  ← Main Flask server (backend logic)
├── dataset.py     ← Script to create the CSV dataset
├── dataset.csv             ← 400 simulated network packets
├── requirements.txt        ← Python libraries needed
│
└── templates/
    └── index.html          ← The web interface (frontend)
```

---

## How to Run the Project

### Step 1 — Install Python Libraries
Open a terminal in this folder and run:
```bash
pip install flask
```

### Step 2 — Generate the Dataset (already done, but you can re-run)
```bash
python generate_dataset.py
```
This creates `dataset.csv` with 200 simulated packets.

### Step 3 — Start the Server
```bash
python app.py
```
You'll see:
```
[INFO] Loaded 400 packets from dataset.csv
[INFO] Starting Flask server at http://127.0.0.1:4500
```

### Step 4 — Open the Web Interface
Go to your browser and visit:
```
http://127.0.0.1:4500
```

### Step 5 — Use the App
1. Click **▶ Start Monitoring** — packets start appearing in the table
2. Use **Filter** dropdowns/textboxes to filter by protocol or IP
3. Click **■ Stop Monitoring** anytime to pause
4. Watch **Statistics** and **Top Source IPs** update in real time

---

## How the Code Works
```

Browser (index.html)
     │
     │  Click "Start"  →  POST /monitor/begin
     │  Every 1 second →  GET  /traffic/fetch
     │                          ↕
     └──────────── Flask Server (app.py)
                          │
                          ├── Reads dataset.csv
                          ├── Runs background thread (adds 1 packet per 0.3s)
                          └── Returns JSON data to browser
```

### Key Concepts Used

| Concept | Where Used |
|---|---|
| CSV file reading | `load_dataset()` in app.py |
| Background thread | `monitoring_loop()` — runs alongside Flask |
| Port → Service mapping | `PORT_SERVICES` dictionary |
| REST API | `/monitor/begin`, `/monitor/halt`, `/traffic/fetch` |
| Filtering | Query params `?protocol=TCP&src_ip=...` |
| Statistics | `compute_statistics()` function |
| Fetch API (JS) | `fetchPackets()` in index.html |

---

## Dataset Fields

| Field | Example | Meaning |
|---|---|---|
| time | 10:35:21 | When packet was captured |
| src_ip | 192.168.1.5 | Sender's IP address |
| dst_ip | 8.8.8.8 | Receiver's IP address |
| protocol | TCP | Communication protocol |
| size | 512 | Packet size in bytes |
| src_port | 52341 | Sender's port (random high port) |
| dst_port | 80 | Receiver's port (tells us the service) |

---

## Common Port → Service Mappings

| Port | Service |
|---|---|
| 80 | HTTP (websites) |
| 443 | HTTPS (secure websites) |
| 53 | DNS (domain name lookup) |
| 22 | SSH (remote login) |
| 25 | SMTP (email sending) |
| 3306 | MySQL (database) |
