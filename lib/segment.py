import struct

# Constants 
SYN_FLAG = 0b00000010
ACK_FLAG = 0b00001000
FIN_FLAG = 0b00000001
DEF_FLAG = 0b00000000

class SegmentFlag:
    def __init__(self, flag : bytes):
        # Init flag variable from flag byte
        if flag == SYN_FLAG:
            self.type = "syn"
        elif flag == ACK_FLAG:
            self.type = "ack"
        elif flag == FIN_FLAG:
            self.type = "fin"

    def get_flag_bytes(self) -> bytes:
        # Convert this object to flag in byte form
        if self.type == "syn":
            return SYN_FLAG
        elif self.type == "ack":
            return ACK_FLAG
        elif self.type == "fin":
            return FIN_FLAG





class Segment:
    # -- Internal Function --
    def __init__(self):
        # Initalize segment
        self.seqNumber = 0
        self.ackNumber = 0
        self.checksum = 0
        self.flag = DEF_FLAG
        self.payload = b""

    def __str__(self):
        # Optional, override this method for easier print(segmentA)
        output = ""
        output += f"{'Sequence number':24} | {self.seqNumber}\n"
        output += f"{'Acknowledgement number':24} | {self.ackNumber}\n"
        output += f"{'Checksum':24} | {self.checksum}\n"
        output += f"{'Flag':24} | {self.flag}\n"
        output += f"{'Payload':24} | {self.payload}\n"
        return output

    def __calculate_checksum(self) -> int:
        # Calculate checksum here, return checksum result
        pass


    # -- Setter --
    def set_header(self, header : dict):
        pass

    def set_payload(self, payload : bytes):
        pass

    def set_flag(self, flag_list : list):
        pass


    # -- Getter --
    def get_flag(self) -> SegmentFlag:
        return SegmentFlag(self.flag)

    def get_header(self) -> dict:
        pass

    def get_payload(self) -> bytes:
        pass


    # -- Marshalling --
    def set_from_bytes(self, src : bytes):
        # From pure bytes, unpack() and set into python variable
        pass

    def get_bytes(self) -> bytes:
        # Convert this object to pure bytes
        pass


    # -- Checksum --
    def valid_checksum(self) -> bool:
        # Use __calculate_checksum() and check integrity of this object
        pass
