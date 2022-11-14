import argparse
import socket
from lib.connection import Connection
from lib.segment import Segment
from lib.logger import Logger
from lib.address import Address
import lib.config as config

class Server:
    def __init__(self, port, path):
        # Init server
        self.filepath = path
        self.ip = config.IP_ADDRESS 
        self.port = port
        self.connection = Connection(self.ip, self.port)
        self.clients = []
        self.logger = Logger("Server")
        self.logger.ok_log(f"[!] Server is running on port {self.port}")

    def listen_for_clients(self):
        # Waiting client for connect
        self.logger.ask_log("[!] Waiting for client to connect...")
        while True:
            seg, addr = self.connection.listen_single_segment()
            addr = Address(addr[0], addr[1])
            self.logger.ask_log(f"[!] Received request from client {addr.ip}:{addr.port}")
            # Echo
            self.connection.send_data(seg, addr.tuple())
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
    def send(self, segment: Segment, address: Address):
        if(segment.payload):
            self.logger.ask_log("[!] Sending segment to client. . .")
        self.connection.send_data(segment, address.tuple())

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

    def three_way_handshake(self, client_addr: Address) -> bool:
        # Three way handshake, server-side, 1 client
        self.logger.ask_log(f"[!] Starting three way handshake with {client_addr.ip}:{client_addr.port}")

        # First phase: send SYN to client
        syn = Segment()
        # Syn flag only
        syn.set_flag([True, False, False])
        if syn.get_flag().syn:
            self.logger.ask_log("SYNNYA KEKIRIM weh")
        self.connection.set_timeout(config.TIMEOUT)
        self.send(syn, client_addr)

        # Second phase: receive SYN-ACK from client

        try:
            try:
                syn_ack, addr = self.connection.listen_single_segment()
                syn_ack_flags = syn_ack.get_flag()
                addr = Address(addr[0], addr[1])
                if syn_ack_flags.syn:
                    self.logger.ok_log(f"[!] Received SYN-ACK from {addr.ip}:{addr.port}")
                if syn_ack_flags.ack:
                    self.logger.ok_log(f"[!] Received ACK from {addr.ip}:{addr.port}")
                if syn_ack_flags.fin:
                    self.logger.ok_log(f"[!] Received FIN from {addr.ip}:{addr.port}")
                if syn_ack_flags.syn and syn_ack_flags.ack:
                    self.logger.ok_log(f"[!] Received SYN-ACK from {addr.ip}:{addr.port}. Handshake phase 2 completed.")

                    # Third phase: send ACK to client
                    ack = Segment()
                    ack.set_flag([False, True, False])
                    self.send(ack, client_addr)
                    self.logger.ok_log(f"[!] Handshake completed with {addr.ip}:{addr.port}")
                else:
                    self.logger.warning_log(f"[!] Received invalid segment from {addr.ip}:{addr.port}. Handshake phase 2 failed.")
                    self.logger.warning_log(f"[!] Exiting..")
                    return False
                
            except Exception as e:
                self.logger.warning_log(f"[!] {e}")
                return False

        except socket.timeout:
            self.logger.warning_log(f"[!] {client_addr.ip}:{client_addr.port} timed out")
            return False

        
        self.logger.ask_log(f"[!] Sending SYN to {client_addr.ip}:{client_addr.port}")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="Server port", type=int)
    parser.add_argument("path", help="File path")
    args = parser.parse_args()
    main = Server(args.port, args.path)
    main.listen_for_clients()
    main.start_file_transfer()
