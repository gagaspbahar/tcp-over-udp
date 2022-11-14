import struct

# Constants 
SYN_FLAG = 0b00000010
ACK_FLAG = 0b00001000
FIN_FLAG = 0b00000001
DEF_FLAG = 0b00000000

class SegmentFlag:
    def __init__(self, flag : bytes):
        # Init flag
        self.syn = False
        self.ack = False
        self.fin = False
        # Init flag variable from flag byte
        if flag & SYN_FLAG:
            self.syn = True
        if flag & ACK_FLAG:
            self.ack = True
        if flag & FIN_FLAG:
            self.fin = True

    def get_flag_bytes(self) -> bytes:
        # Convert this object to flag in byte form
        current_flag = DEF_FLAG
        if self.syn:
            current_flag |= SYN_FLAG
        if self.ack:
            current_flag |= ACK_FLAG
        if self.fin:
            current_flag |= FIN_FLAG
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

    def calculate_checksum(self) -> int:
        # Calculate checksum here, return checksum result
        sum = 0
        data_bytes = self.get_bytes_no_checksum()

        if (len(data_bytes) % 2 != 0):
            data_bytes = b'\x00' + data_bytes
            
        for i in range(0, len(data_bytes), 2):
            sum += int.from_bytes(data_bytes[i:i+2], byteorder='big')
        while sum >> 16:
            sum = (sum & 0xffff) + (sum >> 16)
        return ~sum & 0xffff

    def update_checksum(self):
        # Update checksum value
        self.header['checksum'] = self.calculate_checksum()
        


    # -- Setter --
    def set_header(self, header : dict):
        # Set header from dictionary
        self.header = header
        self.update_checksum()

    def set_payload(self, payload : bytes):
        # Set payload from bytes
        self.payload = payload
        self.update_checksum()

    def set_flag(self, flag_list : list):
        # Set flag from list of flag (SYN, ACK, FIN)
        initial_flag = DEF_FLAG
        if flag_list[0]:
            initial_flag |= SYN_FLAG
        if flag_list[1]:
            initial_flag |= ACK_FLAG
        if flag_list[2]:
            initial_flag |= FIN_FLAG
        self.header['flag'] = initial_flag
        self.update_checksum()


    # -- Getter --
    def get_flag(self) -> SegmentFlag:
        # return flag in segmentflag
        return SegmentFlag(self.header['flag'])

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
        for i in range(5):
            print(i, header_tup[i])
        header = {
            'seqNumber': header_tup[0],
            'ackNumber': header_tup[1],
            'flag': header_tup[2],
            'checksum': header_tup[4]
        }
        self.header = header
        self.payload = src[12:]
        self.update_checksum()

    def get_bytes(self) -> bytes:
        # Convert this object to pure bytes
        header_bytes = struct.pack('iibbH', self.header['seqNumber'], self.header['ackNumber'], self.header['flag'], DEF_FLAG, self.header['checksum'])
        return header_bytes + self.payload

    def get_bytes_no_checksum(self) -> bytes:
        # Get bytes without checksum
        header_bytes = struct.pack('iibb', self.header['seqNumber'], self.header['ackNumber'], self.header['flag'], DEF_FLAG)
        return header_bytes + self.payload

    # -- Checksum --
    def valid_checksum(self) -> bool:
        # Use __calculate_checksum() and check integrity of this object
        return self.calculate_checksum() == self.header['checksum']

# if __name__ == '__main__':
#     segment = Segment()
#     segment.header['seqNumber'] = 1
#     segment.header['ackNumber'] = 2
#     segment.header['flag'] = SYN_FLAG
#     segment.payload = b"Hello World"
#     segment.update_checksum()
#     print(segment.calculate_checksum())
#     if segment.valid_checksum():
#         print("Checksum valid")
#     else:
#         print("Checksum invalid")
#     print(segment.get_bytes_no_checksum().hex())
#     print(segment.get_bytes().hex())