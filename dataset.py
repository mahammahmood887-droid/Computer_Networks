import csv
import random
from datetime import datetime, timedelta

INTERNAL_IPS = [
    "192.168.1.5", "192.168.1.10", "192.168.1.15",
    "192.168.1.20", "192.168.0.100", "10.0.0.5",
    "10.0.0.12", "172.16.0.3",
]

EXTERNAL_IPS = [
    "8.8.8.8", "1.1.1.1", "142.250.80.46",
    "104.21.45.10", "151.101.1.69", "13.107.42.14",
    "52.86.34.120", "185.60.216.35",
]

PROTOCOLS = ["TCP"] * 60 + ["UDP"] * 30 + ["ICMP"] * 10

PORT_PAIRS = [
    (random.randint(49152, 65535), 80),
    (random.randint(49152, 65535), 443),
    (random.randint(49152, 65535), 53),
    (random.randint(49152, 65535), 22),
    (random.randint(49152, 65535), 25),
    (random.randint(49152, 65535), 3306),
    (random.randint(49152, 65535), 8080),
]

def random_time(start_hour=10, total_minutes=30):
    base = datetime(2024, 1, 1, start_hour, 0, 0)
    delta = timedelta(seconds=random.randint(0, total_minutes * 60))
    t = base + delta
    return t.strftime("%H:%M:%S")

def generate_packet(packet_id):
    protocol = random.choice(PROTOCOLS)
    src_ip = random.choice(INTERNAL_IPS)
    dst_ip = random.choice(EXTERNAL_IPS)

    if protocol == "ICMP":
        src_port = 0
        dst_port = 0
        size = random.randint(28, 84)
    elif protocol == "UDP":
        src_port = random.randint(49152, 65535)
        dst_port = random.choice([53, 67, 123, 5353])
        size = random.randint(64, 512)
    else:
        pair = random.choice(PORT_PAIRS)
        src_port = random.randint(49152, 65535)
        dst_port = pair[1]
        size = random.randint(64, 1500)

    return {
        "id": packet_id,
        "time": random_time(),
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "protocol": protocol,
        "size": size,
        "src_port": src_port,
        "dst_port": dst_port,
    }

NUM_PACKETS = 400

with open("dataset.csv", "w", newline="") as f:
    fieldnames = ["id", "time", "src_ip", "dst_ip",
                  "protocol", "size", "src_port", "dst_port"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for i in range(1, NUM_PACKETS + 1):
        writer.writerow(generate_packet(i))

print(f"[DONE] Generated {NUM_PACKETS} packets → dataset.csv")