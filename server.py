import argparse
from lib.connection import Connection
from lib.segment import Segment
from lib.logger import Logger
from lib.address import Address

class Server:
    def __init__(self, port, path):
        # Init server
        self.filepath = path
        self.ip = "localhost"
        self.port = port
        self.connection = Connection(self.ip, self.port)
        self.clients = []
        self.logger = Logger("Server")
        self.logger.ok_log("[!] Server is running on port", self.port)

    def listen_for_clients(self):
        # Waiting client for connect
        while True:
            seg, addr = self.connection.listen_single_segment()
            addr = Address(addr[0], addr[1])
            self.logger.ask_log(f"[!] Received request from client {addr.ip}:{addr.port}")
            # Echo
            self.connection.send_data(seg, addr)
            self.clients.append(addr)
            self.logger.ask_log("[?] Listen more? (y/n)")
            if input() == "y":
                continue
            else:
                break
        if len(self.clients):
            self.logger.ok_log(f"[!] {len(self.clients)} clients connected.")
            print("Client list:")
            for i in range(len(self.clients)):
                print(f"{i+1}. {self.clients[i].ip}:{self.clients[i].port}")

    # Server kirim file ke client
    def send(self, segment: Segment, index: int):
        if(segment.payload):
            self.logger.ask_log("[!] Sending segment to client. . .")
        self.connection.send_data(segment, self.clients[index])

    def receive(self):
        segment, addr = self.connection.listen_single_segment()
        if (segment.payload):
            self.logger.ask_log(f"[!] Receiving segment from {addr.ip}:{addr.port}")
        else: 
            #lov u kak -gagas lyo clau <3
            pass
            

    def start_file_transfer(self):
        # Handshake & file transfer for all client
        if len(self.clients) == 0:
            self.logger.warning_log("[!] No client connected, exiting...")
            return
        else:
            self.logger.ask_log("[!] Starting file transfer...")
            for client in self.clients:
                self.logger.ask_log(f"[!] Commencing handshake with {client.ip}:{client.port}")
                status = self.three_way_handshake(client)
                if status:
                    self.logger.ask_log(f"[!] Sending file to {client.ip}:{client.port}")
                    self.file_transfer(client)
                else:
                    self.logger.warning_log(f"[!] Handshake failed with {client.ip}:{client.port}")

    def file_transfer(self, client_addr : "tuple['str', 'int']"):
        # File transfer, server-side, Send file to 1 client
        pass

    def three_way_handshake(self, client_addr: "tuple['str', 'int']") -> bool:
       # Three way handshake, server-side, 1 client

       pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="Server port", type=int)
    parser.add_argument("path", help="File path")
    args = parser.parse_args()
    main = Server(args.port, args.path)
    main.listen_for_clients()
    main.start_file_transfer()
