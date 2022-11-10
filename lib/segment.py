import struct

# Constants 
SYN_FLAG = 0b00000010
ACK_FLAG = 0b00001000
FIN_FLAG = 0b00000001
DEF_FLAG = 0b00000000

class SegmentFlag:
    def __init__(self, flag : bytes):
        # Init flag variable from flag byte
        if flag & SYN_FLAG != 0:
            self.syn = True
        if flag & ACK_FLAG != 0:
            self.ack = True
        if flag & FIN_FLAG != 0:
            self.fin = True

    def get_flag_bytes(self) -> bytes:
        # Convert this object to flag in byte form
        current_flag = DEF_FLAG
        if self.syn:
            current_flag = DEF_FLAG | SYN_FLAG
        if self.ack:
            current_flag = DEF_FLAG | ACK_FLAG
        if self.fin:
            current_flag = DEF_FLAG | FIN_FLAG
        return current_flag





class Segment:
    # -- Internal Function --
    def __init__(self):
        # Initalize segment
        self.header = {}
        self.header['seqNumber'] = 0
        self.header['ackNumber'] = 0
        self.header['checksum'] = 0
        self.header['flag'] = DEF_FLAG
        self.payload = b""

    def __str__(self):
        # Optional, override this method for easier print(segmentA)
        output = ""
        output += f"{'Sequence number':24} | {self.header['seqNumber']}\n"
        output += f"{'Acknowledgement number':24} | {self.header['ackNumber']}\n"
        output += f"{'Checksum':24} | {self.header['checksum']}\n"
        output += f"{'Flag':24} | {self.header['flag']}\n"
        output += f"{'Payload':24} | {self.payload}\n"
        return output

    def __calculate_checksum(self) -> int:
        # Calculate checksum here, return checksum result
        pass

    def update_checksum(self):
        # Update checksum value
        self.checksum = self.__calculate_checksum()


    # -- Setter --
    def set_header(self, header : dict):
        # Set header from dictionary
        self.header = header
        self.update_checksum

    def set_payload(self, payload : bytes):
        # Set payload from bytes
        self.payload = payload
        self.update_checksum()

    def set_flag(self, flag_list : list):
        # Set flag from list of flag (SYN, ACK, FIN)
        initial_flag = DEF_FLAG
        if flag_list[0]:
            self.flag = initial_flag | SYN_FLAG
        if flag_list[1]:
            self.flag = initial_flag | ACK_FLAG
        if flag_list[2]:
            self.flag = initial_flag | FIN_FLAG
        pass


    # -- Getter --
    def get_flag(self) -> SegmentFlag:
        # return flag in segmentflag
        return SegmentFlag(self.flag)

    def get_header(self) -> dict:
        # Return header in dictionary form
        return self.header

    def get_payload(self) -> bytes:
        # Return payload in bytes
        return self.payload

    # -- Marshalling --
    def set_from_bytes(self, src : bytes):
        # From pure bytes, unpack() and set into python variable
        # 44112: iibbh
        header_bytes = src[:12]
        header_tup = struct.unpack('iibbh', header_bytes)
        header = {
            'seqNumber': header_tup[0],
            'ackNumber': header_tup[1],
            'flag': header_tup[2],
            'checksum': header_tup[4]
        }
        self.header = header
        self.payload = src[12:]

    def get_bytes(self) -> bytes:
        # Convert this object to pure bytes
        header_bytes = struct.pack('iibbh', self.header['seqNumber'], self.header['ackNumber'], self.header['flag'], DEF_FLAG, self.header['checksum'])
        return header_bytes + self.payload


    # -- Checksum --
    def valid_checksum(self) -> bool:
        # Use __calculate_checksum() and check integrity of this object
        pass
