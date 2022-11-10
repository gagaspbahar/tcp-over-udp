import argparse
from lib.connection import Connection
from lib.logger import Logger
from lib.segment import Segment

class Client:
    def __init__(self, port, server_port, path):
        # Init client
        self.port = port
        self.ip = "localhost"
        self.server_port = server_port
        self.filepath = path
        self.connection = Connection(self.ip, self.port)
        self.logger = Logger("Client")
        self.logger.ok_log("[!] Client started at port", self.port)

    # def send(self, segment: Segment):
    #     if(segment.payload):
    #         print("[!]")



    def three_way_handshake(self):
        # Three Way Handshake, client-side
        pass

    def listen_file_transfer(self):
        # File transfer, client-side
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="Client port", type=int)
    parser.add_argument("server_port", help="Server port", type=int)
    parser.add_argument("path", help="Output file path")
    args = parser.parse_args()
    main = Client(args.port, args.server_port, args.path)
    main.three_way_handshake()
    main.listen_file_transfer()
