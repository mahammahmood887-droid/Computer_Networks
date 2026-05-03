from flask import Flask, jsonify, request, render_template
import csv
import time
import threading
import os

app = Flask(__name__)

all_packets = []
captured_packets = []
monitoring = False
monitor_thread = None
packet_index = 0

PORT_SERVICES = {
    80: "HTTP",
    443: "HTTPS",
    53: "DNS",
    22: "SSH",
    21: "FTP",
    25: "SMTP",
    110: "POP3",
    143: "IMAP",
    3306: "MySQL",
    5432: "PostgreSQL",
    8080: "HTTP-Alt",
    3389: "RDP",
    23: "Telnet",
    67: "DHCP",
    123: "NTP",
}

def get_service(port):
    try:
        return PORT_SERVICES.get(int(port), "Unknown")
    except:
        return "Unknown"


def load_dataset(filepath="dataset.csv"):
    global all_packets
    all_packets = []

    if not os.path.exists(filepath):
        print(f"[WARNING] Dataset file '{filepath}' not found.")
        return

    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            packet = {
                "id": i + 1,
                "time": row.get("time", ""),
                "src_ip": row.get("src_ip", ""),
                "dst_ip": row.get("dst_ip", ""),
                "protocol": row.get("protocol", "").upper(),
                "size": row.get("size", "0"),
                "src_port": row.get("src_port", "0"),
                "dst_port": row.get("dst_port", "0"),
                "service": get_service(row.get("dst_port", "0")),
            }
            all_packets.append(packet)

    print(f"[INFO] Loaded {len(all_packets)} packets from dataset.")


def monitoring_loop():
    global captured_packets, monitoring, packet_index

    while monitoring and packet_index < len(all_packets):
        packet = all_packets[packet_index]
        captured_packets.append(packet)
        packet_index += 1
        time.sleep(0.3)

    monitoring = False


def compute_statistics(packets):
    if not packets:
        return {
            "total": 0,
            "tcp": 0, "udp": 0, "icmp": 0, "other": 0,
            "avg_size": 0,
            "top_sources": []
        }

    total = len(packets)
    tcp = sum(1 for p in packets if p["protocol"] == "TCP")
    udp = sum(1 for p in packets if p["protocol"] == "UDP")
    icmp = sum(1 for p in packets if p["protocol"] == "ICMP")
    other = total - tcp - udp - icmp

    sizes = []
    for p in packets:
        try:
            sizes.append(int(p["size"]))
        except:
            sizes.append(0)
    avg_size = round(sum(sizes) / total, 1) if total > 0 else 0

    from collections import Counter
    src_counter = Counter(p["src_ip"] for p in packets)
    top_sources = [{"ip": ip, "count": cnt}
                   for ip, cnt in src_counter.most_common(5)]

    return {
        "total": total,
        "tcp": tcp,
        "udp": udp,
        "icmp": icmp,
        "other": other,
        "avg_size": avg_size,
        "top_sources": top_sources,
    }


# ✅ FIXED ROUTE
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/monitor/begin", methods=["POST"])
def start_monitoring():
    global monitoring, monitor_thread, captured_packets, packet_index

    if monitoring:
        return jsonify({"status": "already_running"})

    captured_packets = []
    packet_index = 0
    monitoring = True

    monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
    monitor_thread.start()

    return jsonify({"status": "started"})


@app.route("/monitor/halt", methods=["POST"])
def stop_monitoring():
    global monitoring
    monitoring = False
    return jsonify({"status": "stopped"})


@app.route("/traffic/fetch", methods=["GET"])
def get_packets():
    protocol = request.args.get("protocol", "").upper()
    src_ip = request.args.get("src_ip", "").strip()
    dst_ip = request.args.get("dst_ip", "").strip()

    results = captured_packets[:]

    if protocol and protocol != "ALL":
        results = [p for p in results if p["protocol"] == protocol]
    if src_ip:
        results = [p for p in results if src_ip in p["src_ip"]]
    if dst_ip:
        results = [p for p in results if dst_ip in p["dst_ip"]]

    return jsonify({
        "packets": results,
        "stats": compute_statistics(captured_packets),
        "monitoring": monitoring,
        "total_in_dataset": len(all_packets),
    })


@app.route("/api/status", methods=["GET"])
def get_status():
    return jsonify({
        "monitoring": monitoring,
        "captured": len(captured_packets),
    })


if __name__ == "__main__":
    load_dataset("dataset.csv")
    print("[INFO] Starting Flask server at http://127.0.0.1:4500")
    app.run(port=4500,debug=True, use_reloader=False)