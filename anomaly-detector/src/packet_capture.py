from scapy.all import sniff

class PacketCapture:
    def __init__(self, packet_handler):
        self.packet_handler = packet_handler

    def start_capture(self, interface="eth0", bpf_filter="tcp port 502"):
        sniff(
            iface=interface,
            prn=self.packet_handler,
            store=0,
            filter=bpf_filter,
        )