import json
from pathlib import Path
from scapy.all import rdpcap

from traffic_analyzer import TrafficAnalyzer


def main():
    pcap_path = Path(
        r"C:\Users\ameli\OneDrive\Documents\combitech\Modbus Dataset\Modbus Dataset\benign\scada-hmi\scada-hmi-network-capture\veth5bbeaa2-normal-13.pcap"
    )

    analyzer = TrafficAnalyzer()

    print(f"Loading PCAP: {pcap_path}")
    packets = rdpcap(str(pcap_path))
    print(f"Total packets in file: {len(packets)}\n")

    parsed_count = 0

    """for i, packet in enumerate(packets, start=1):
        event = analyzer.analyze_packet(packet)
        if event is not None:
            parsed_count += 1
            print(f"Event {parsed_count} (packet #{i}):")
            print(json.dumps(event, indent=2))
            print("-" * 60)
"""
    for i, packet in enumerate(packets, start=1):
        event = analyzer.analyze_packet(packet)
        if event is not None:
            parsed_count += 1
            print(json.dumps(event, indent=2))
            print("-" * 60)

        if parsed_count >= 10:
            break

    print(f"\nFinished.")
    print(f"Packets in file: {len(packets)}")
    print(f"Parsed Modbus/TCP events: {parsed_count}")


if __name__ == "__main__":
    main()