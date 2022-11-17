import argparse
import socket
from lib.connection import Connection
from lib.segment import Segment
from lib.logger import Logger
from lib.address import Address
import lib.config as config
import lib.util as util

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
        self.clients = []
        try:
            while True:
                self.logger.ask_log("[!] Waiting for client to connect...")
                self.connection.set_timeout(99999)
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
                self.logger.ok_log("Client list:")
                for i in range(len(self.clients)):
                    print(f"{i+1}. {self.clients[i].ip}:{self.clients[i].port}")
                self.start_file_transfer()
        except socket.timeout:
            self.logger.warning_log("[!] Timeout. Exiting...")
            return

    # Server kirim file ke client
    def send(self, segment: Segment, address: Address):                                             
        self.connection.send_data(segment, address.tuple())

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
            self.logger.ask_log("[!] Listen more? (y/n)")
            if input() == "y":
                self.listen_for_clients()
            else:
                self.logger.ask_log("[!] Closing server...")
                return


    def file_transfer(self, client_addr : "tuple['str', 'int']"):
        # File transfer, server-side, Send file to 1 client
        self.logger.ask_log("[!] Initiating file transfer...")
        filebytes = open(self.filepath, "rb").read()
        byte_array = util.partition_data(filebytes)

        N = config.WINDOW_SIZE
        segment_number = 0
        segment_base = 0
        sequence_max = N - 1
        
        segment_count = len(byte_array)

        while True:
            # Send N segment
            while segment_base <= segment_number <= sequence_max and segment_number < segment_count:
                segment = Segment()
                segment.set_seq_number(segment_number)
                if segment_number >= len(byte_array):
                    break
                segment.set_payload(byte_array[segment_number])
                self.send(segment, client_addr)
                self.logger.ask_log(f"[!] Sending segment {segment_number} to client {client_addr.ip}:{client_addr.port}")
                segment_number += 1

            # Receive ACK
            self.connection.set_timeout(config.TIMEOUT)
            try:
                ack, addr = self.connection.listen_single_segment()
                ack_flags = ack.get_flag()
                addr = Address(addr[0], addr[1])
                ack_number = ack.get_header()['ackNumber']
                if ack_flags.ack:
                    self.logger.ok_log(f"[!] Received ACK from {addr.ip}:{addr.port} with ackNumber {ack_number}")
                    
                    segment_base = ack_number
                    sequence_max = segment_base + (N - 1)
                    if segment_base + 1 == segment_count:
                        break
                    else:
                        continue
                else:
                    self.logger.warning_log(f"[!] Received invalid segment from {addr.ip}:{addr.port}")
                    self.logger.warning_log(f"[!] Exiting..")
                    raise Exception("Invalid segment received")
            except socket.timeout:
                self.logger.warning_log(f"[!] {client_addr.ip}:{client_addr.port} timed out")
                segment_number = segment_base
                continue
            except Exception as e:
                self.logger.warning_log(f"[!] {e}")
                segment_number = segment_base
                continue
        
            
        # Done
        self.logger.ok_log(f"[!] File transfer complete")
        self.logger.ok_log(f"[!] Closing connection with {client_addr.ip}:{client_addr.port}")
        self.close_connection(client_addr)

        
    def close_connection(self, client_addr : Address):
        # Send FIN to client
        while True:
            self.logger.ask_log(f"[!] Sending FIN to {client_addr.ip}:{client_addr.port}")
            fin = Segment()
            fin.set_flag([False, False, True])
            self.send(fin, client_addr)
            self.logger.ask_log(f"[!] Waiting for ACK from {client_addr.ip}:{client_addr.port}")
            try:
                ack, addr = self.connection.listen_single_segment()
                ack_flags = ack.get_flag()
                addr = Address(addr[0], addr[1])
                if ack_flags.ack:
                    self.logger.ok_log(f"[!] Received ACK from {addr.ip}:{addr.port}")
                    break
                else:
                    self.logger.warning_log(f"[!] Received invalid segment from {addr.ip}:{addr.port}")
                    self.logger.warning_log(f"[!] Exiting..")
                    raise Exception("Invalid segment received")
            except socket.timeout:
                self.logger.warning_log(f"[!] {client_addr.ip}:{client_addr.port} timed out. Resending FIN")
                continue
            except Exception as e:
                self.logger.warning_log(f"[!] {e}")
                self.logger.warning_log("[!] ACK not received. Exiting..")
                return
            


    def three_way_handshake(self, client_addr: Address) -> bool:
        # Three way handshake, server-side, 1 client
        self.logger.ask_log(f"[!] Starting three way handshake with {client_addr.ip}:{client_addr.port}")

        # First phase: send SYN to client
        syn = Segment()
        # Syn flag only
        syn.set_flag([True, False, False])
        self.connection.set_timeout(config.TIMEOUT)
        self.send(syn, client_addr)

        # Second phase: receive SYN-ACK from client

        try:
            try:
                syn_ack, addr = self.connection.listen_single_segment()
                syn_ack_flags = syn_ack.get_flag()
                addr = Address(addr[0], addr[1])
                if syn_ack_flags.syn and syn_ack_flags.ack:
                    self.logger.ok_log(f"[!] Received SYN-ACK from {addr.ip}:{addr.port}. Handshake phase 2 completed.")

                    # Third phase: send ACK to client
                    ack = Segment()
                    ack.set_flag([False, True, False])
                    self.send(ack, client_addr)
                    self.logger.ok_log(f"[!] Handshake completed with {addr.ip}:{addr.port}")
                    return True
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

        



# Main driver
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="Server port", type=int)
    parser.add_argument("path", help="File path")
    args = parser.parse_args()
    main = Server(args.port, args.path)
    main.listen_for_clients()
