from scapy.all import IP, TCP, Raw
from traffic_analyzer import TrafficAnalyzer

analyzer = TrafficAnalyzer()

def create_modbus_packet(src, dst, sport, dport, function_code):
    # Minimal Modbus/TCP payload (MBAP + function code)
    payload = (
        b'\x00\x01'      # Transaction ID
        b'\x00\x00'      # Protocol ID (must be 0)
        b'\x00\x06'      # Length
        b'\x01'          # Unit ID
        + bytes([function_code])  # Function code
    )

    return IP(src=src, dst=dst) / TCP(sport=sport, dport=dport) / Raw(load=payload)


# Simulated traffic
test_packets = [
    create_modbus_packet("192.168.1.10", "192.168.1.20", 12345, 502, 3),
    create_modbus_packet("192.168.1.10", "192.168.1.20", 12345, 502, 3),
    create_modbus_packet("192.168.1.10", "192.168.1.20", 12345, 502, 6),  # write
]

print("Testing synthetic Modbus traffic...\n")

for i, pkt in enumerate(test_packets):
    event = analyzer.analyze_packet(pkt)
    print(f"Packet {i+1}:")
    print(event)
    print("-" * 50)