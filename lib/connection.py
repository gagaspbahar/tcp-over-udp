import socket
from .segment import Segment

class Connection:
    def __init__(self, ip : str, port : int):
        # Init UDP socket
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))

    def send_data(self, msg : Segment, dest : "tuple['str', 'int']"):
        # Send single segment into destination
        self.socket.sendto(msg.get_bytes(), dest)

    def listen_single_segment(self) -> tuple(Segment, "tuple['str', 'int']"):
        # Listen single UDP datagram within timeout and convert into segment
        msg, addr = self.socket.recvfrom(32768)
        segment = Segment()
        segment.set_bytes(msg)
        if not segment.valid_checksum():
            raise Exception("Invalid checksum.")
        return segment, addr

    def close_socket(self):
        # Release UDP socket
        self.socket.close()
