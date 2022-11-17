import argparse
import socket
from lib.connection import Connection
from lib.logger import Logger
from lib.segment import Segment
import lib.config as config
import lib.util as util

class Client:
    def __init__(self, port, server_port, path):
        # Init client
        self.port = port
        self.ip = config.IP_ADDRESS
        self.server_port = server_port
        self.filepath = path
        self.file = []
        self.connection = Connection(self.ip, self.port)
        self.logger = Logger("Client")
        self.logger.ok_log(f"[!] Client started at port {self.port}")

    def send(self, segment: Segment):
        # Send segment to server
        self.connection.send_data(segment, (self.ip, self.server_port))

    def request_to_server(self):
        self.logger.ok_log("[!] Searching for server..")
        segment = Segment()
        segment.set_flag([True, True, True])
        self.connection.set_timeout(config.TIMEOUT)
        while True:
            self.send(segment)
            self.logger.ask_log("[!] Sending request to server..")
            try:
                _, addr = self.connection.listen_single_segment()
                
                if addr:
                    self.logger.ok_log(f"[!] Server found at {addr[0]}:{addr[1]}")
                    return addr
            except socket.timeout:
                self.logger.warning_log("[!] Server timed out, listening again..")
        

    def three_way_handshake(self):
        # Three Way Handshake, client-side
        self.logger.ask_log("[!] Commencing handshake with server...")
        self.logger.ask_log("[!] Listening for SYN..")
        while True:
            try:
                syn, _ = self.connection.listen_single_segment()
                syn_flags = syn.get_flag()
                if syn_flags.syn:
                    self.logger.ok_log("[!] SYN received.")
                    break
                else:
                    self.logger.warning_log("[!] Segment is not SYN, listening again..")
            except socket.timeout:
                self.logger.warning_log("[!] Server timed out, listening again..")
                
        
        # Phase 2: Send SYN-ACK
        syn_ack = Segment()
        syn_ack.set_flag([True, True, False])
        self.connection.set_timeout(config.TIMEOUT)
        self.send(syn_ack)
        self.logger.ask_log("[!] Sending SYN-ACK to server..")

        # Phase 3: Receive ACK
        while True:
            try:
                ack, _ = self.connection.listen_single_segment()
                ack_flags = ack.get_flag()
                if ack_flags.ack:
                    self.logger.ok_log("[!] ACK received.")
                    break
                else:
                    self.logger.warning_log("[!] Segment is not ACK, listening again..")
            except socket.timeout:
                exit(1)
        

    def listen_file_transfer(self):
        # File transfer, client-side
        self.logger.ask_log("[!] Receiving segment from server ...")

        # Go Back N
        N = config.WINDOW_SIZE
        Rn = 0
        Sn = 0
        Sb = 0

        while True: 
            self.connection.set_timeout(config.TIMEOUT)
            
            try: 
                file_segment, _ = self.connection.listen_single_segment()
                Sn = file_segment.get_header()['seqNumber']
                flag = file_segment.get_flag()

                # if there is no more data from the sender (FIN flag)
                if (flag.fin): 
                    byte_array_received = util.join_data(self.file)
                    file_received = open(self.filepath, "wb")
                    file_received.write(byte_array_received)
                    file_received.close()
                    self.logger.ok_log("[!] File received.")
                    ack = Segment()
                    ack.set_flag([False, True, False])
                    self.send(ack)
                    self.logger.ask_log("[!] Sending ACK to server. Closing connection... Happy to know you <3")
                    break
                
                # if the segment received less than or equal to Rn and the segment is error free then
                if (Sn <= Rn):
                    # Accept the segment
                    # Send segment to a higher layer
                    last_received = len(self.file) - 1

                    # Handle file order when ACK Lost
                    if (last_received == Sn - 1):
                        self.file.append(file_segment.get_payload())
                        self.logger.ok_log(f"[!] Segment {Sn} received and added to buffer.")
                        
                    # Send ACK
                    ack = Segment()
                    ack.set_ack_number(Sn)
                    ack.set_flag([False, True, False])
                    
                    # Rn := Rn + 1
                    self.logger.ask_log(f"[!] Sending ACK to server. Sequence number = {Sn}")
                    self.send(ack)
                    Rn = len(self.file) + 1

                else:
                    # Refuse segment
                    self.logger.warning_log(f"[!] Segment number {Sn} refused. Expected number: {Rn}. Timing out..")

                # Send acknowledgement for last received segment
                    
            
            except Exception as e:
                self.logger.warning_log(f"[!] {e}")
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="Client port", type=int)
    parser.add_argument("server_port", help="Server port", type=int)
    parser.add_argument("path", help="Output file path")
    args = parser.parse_args()
    main = Client(args.port, args.server_port, args.path)
    main.request_to_server()
    main.three_way_handshake()
    main.listen_file_transfer()
