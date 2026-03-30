from scapy.all import sniff, IP, TCP, Raw
from collections import defaultdict

MODBUS_PORT = 502

MODBUS_FUNCTION_CODES = {
    1: "read_coils",
    2: "read_discrete_inputs",
    3: "read_holding_registers",
    4: "read_input_registers",
    5: "write_single_coil",
    6: "write_single_register",
    15: "write_multiple_coils",
    16: "write_multiple_registers"
}

class TrafficAnalyzer:
    def __init__(self):
        self.traffic_stats = defaultdict(
            lambda: {
                "packet_count": 0,
                "byte_count": 0,
                "start_time": None,
                "last_time": None,
            }
        )
        
        self.last_timestamp = {}
    
    def analyze_packet(self, packet):
        """
        this function parses apckets and returns a dictionary of events from Modbus/TCP.
        None is returned if packet is not tcp/ip, not related to modbus, or 
        doesn't contain enough payload
        """
        if IP not in packet or TCP not in packet:
            return None

        tcp = packet[TCP]

        if tcp.sport != MODBUS_PORT and tcp.dport != MODBUS_PORT:
            return None

        if Raw not in packet:
            return None

        payload = bytes(packet[Raw].load)

        if len(payload) < 8:
            return None

        modbus_fields = self.parse_modbus_tcp(payload)
        if modbus_fields is None:
            return None

        ip_src = packet[IP].src
        ip_dst = packet[IP].dst
        port_src = tcp.sport
        port_dst = tcp.dport
        current_time = float(packet.time)

        direction, is_request = self.infer_directions(port_src, port_dst)

        traffic_key = (ip_src, ip_dst, modbus_fields["function_code"])

        stats = self.traffic_stats[traffic_key]
        stats["packet_count"] += 1
        stats["byte_count"] += len(packet)

        if stats["start_time"] is None:
            stats["start_time"] = current_time

        previous_time = self.last_timestamp.get(traffic_key)
        interval_from_last_packet = None

        if previous_time is not None:
            interval_from_last_packet = current_time - previous_time

        stats["last_time"] = current_time
        self.last_timestamp[traffic_key] = current_time

        return self.extract_stats(
            packet=packet,
            stats=stats,
            modbus_fields=modbus_fields,
            ip_src=ip_src,
            ip_dst=ip_dst,
            port_src=port_src,
            port_dst=port_dst,
            current_time=current_time,
            direction=direction,
            is_request=is_request,
            interval_since_last=interval_from_last_packet, 
        )
    
    def infer_directions(self, port_src, port_dst):
        if port_dst == MODBUS_PORT:
            return "client_to_plc", True
        if port_src == MODBUS_PORT:
            return "plc_to_client", False
        return "unknown", None
    
    def parse_modbus_tcp(self, payload):
        """
        Parse the Modbus/TCP MBAP header and function code.

        MBAP format:
        - transaction_id: 2 bytes
        - protocol_id: 2 bytes
        - length: 2 bytes
        - unit_id: 1 byte
        - function_code: 1 byte
        """
        if len(payload) < 8:
            return None

        transaction_id = int.from_bytes(payload[0:2], byteorder="big")
        protocol_id = int.from_bytes(payload[2:4], byteorder="big")
        length_field = int.from_bytes(payload[4:6], byteorder="big")
        unit_id = payload[6]
        function_code = payload[7]

        # For Modbus/TCP, protocol_id should be 0
        if protocol_id != 0:
            return None

        # Exception responses use function_code + 128
        is_exception = function_code > 127
        base_function_code = function_code - 128 if is_exception else function_code

        function_name = MODBUS_FUNCTION_CODES.get(base_function_code, "unknown")

        return {
            "transaction_id": transaction_id,
            "protocol_id": protocol_id,
            "length": length_field,
            "unit_id": unit_id,
            "function_code": base_function_code,
            "raw_function_code": function_code,
            "function_name": function_name,
            "is_exception": is_exception,
        }

    def extract_stats(
        self,
        packet,
        stats,
        modbus_fields,
        ip_src,
        ip_dst,
        port_src,
        port_dst,
        current_time,
        direction,
        is_request,
        interval_since_last,
    ):
        """
        Build event dictionary from parsed packet and running traffic stats.
        """
        flow_duration = 0.0
        packet_rate = 0.0
        byte_rate = 0.0

        if stats["start_time"] is not None and stats["last_time"] is not None:
            flow_duration = stats["last_time"] - stats["start_time"]
            if flow_duration > 0:
                packet_rate = stats["packet_count"] / flow_duration
                byte_rate = stats["byte_count"] / flow_duration

        return {
            "timestamp": current_time,
            "src_ip": ip_src,
            "dst_ip": ip_dst,
            "src_port": port_src,
            "dst_port": port_dst,
            "packet_size": len(packet),
            "direction": direction,
            "is_request": is_request,
            "pair_key": f"{ip_src}->{ip_dst}",
            "flow_key": f"{ip_src}->{ip_dst}:fc{modbus_fields['function_code']}",
            "transaction_id": modbus_fields["transaction_id"],
            "unit_id": modbus_fields["unit_id"],
            "function_code": modbus_fields["function_code"],
            "raw_function_code": modbus_fields["raw_function_code"],
            "function_name": modbus_fields["function_name"],
            "is_exception": modbus_fields["is_exception"],
            "interval_since_last": interval_since_last,
            "flow_packet_count": stats["packet_count"],
            "flow_byte_count": stats["byte_count"],
            "flow_duration": flow_duration,
            "packet_rate": packet_rate,
            "byte_rate": byte_rate,
        }