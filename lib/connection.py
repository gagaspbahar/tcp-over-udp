import socket
from .segment import Segment
from .address import Address


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

    def listen_single_segment(self) -> tuple([Segment, Address]):
        # Listen single UDP datagram within timeout and convert into segment
        msg, addr = self.socket.recvfrom(32768)
        segment = Segment()
        print("msg: ", msg)
        segment.set_from_bytes(msg)
        if not segment.valid_checksum():
            raise Exception("Invalid checksum.")
        return segment, addr
    
    def set_timeout(self, int):
        # Set timeout for socket
        self.socket.settimeout(int)

    def close_socket(self):
        # Release UDP socket
        self.socket.close()
