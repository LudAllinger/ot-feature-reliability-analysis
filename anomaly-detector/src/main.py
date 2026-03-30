import json

from packet_capture import PacketCapture
from traffic_analyzer import TrafficAnalyzer


def main():
    analyzer = TrafficAnalyzer()

    def handle_packet(packet):
        event = analyzer.analyze_packet(packet)
        if event is not None:
            print(json.dumps(event, indent=2))

    capture = PacketCapture(packet_handler=handle_packet)

    interface = "eth0"

    print(f"Starting Modbus/TCP capture on interface '{interface}'")
    print("Press Ctrl+C to stop.")

    try:
        capture.start_capture(interface=interface, bpf_filter="tcp port 502")
    except KeyboardInterrupt:
        print("\nCapture stopped.")


if __name__ == "__main__":
    main()