import json
import os
from pathlib import Path
from datetime import datetime
from packet_capture import PacketCapture
from traffic_analyzer import TrafficAnalyzer

BASE     = Path(__file__).resolve().parents[2]
LOG_FILE = BASE / "logs" / "network" / "normal" / "network_log.csv"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def main():
    analyzer = TrafficAnalyzer()
    
    if not LOG_FILE.exists():
        with open(LOG_FILE, "w") as f:
            f.write("timestamp,src_ip,dst_ip,function_code,packet_rate,interval_since_last\n")

    log_f = open(LOG_FILE, "a")

    def handle_packet(packet):
        event = analyzer.analyze_packet(packet)
        if event is not None:
            #print(json.dumps(event, indent=2))
            timestamp = datetime.fromtimestamp(event['timestamp']).isoformat()

            log_f.write(
                f"{timestamp},{event['src_ip']},{event['dst_ip']},"
                f"{event['function_code']},{event['packet_rate']},{event['interval_since_last']}\n"
            )
            log_f.flush()

    capture = PacketCapture(packet_handler=handle_packet)

    ## network interface name
    # interface = "eth0"
    interface = r"\Device\NPF_Loopback"

    print(f"Starting Modbus/TCP capture on interface '{interface}'")
    print("Press Ctrl+C to stop.")

    try:
        capture.start_capture(interface=interface, bpf_filter="tcp port 502")
    except KeyboardInterrupt:
        print("\nCapture stopped.")
    finally:
        log_f.close()


if __name__ == "__main__":
    main()