import socket
import struct

ICMP_ECHO_REPLY = 0
ICMP_ECHO_REQUEST = 8

class ICMPPacket(object):
    def __init__(self, icmp_type, icmp_code, data, dest=(None, None)):
        """
        This function only support Echo Request and Echo Reply type
        """
        self.type, self.code = icmp_type, icmp_code
        self.checksum = None
        self.data = data
        self.dest = dest
        self.length = len(self.data)

    def build_raw_icmp(self):
        pack_str = "!BBHHH4sH"
        print(self.dest[0])
        pack_args = [self.type, self.code, 0, 0, 0,
                     socket.inet_aton(self.dest[0]), self.dest[1]]
        if self.length:
            pack_str += "{}s".format(self.length)
            pack_args.append(self.data)

        self.checksum = icmp_checksum(struct.pack(pack_str, *pack_args)) 
        pack_args[2] = self.checksum
        return struct.pack(pack_str, *pack_args)

    
def parse_tcp_packet(packet):
    ip_pack_str = "BBHHHBBH4s4s"
    icmp_pack_str = "!BBHHH4sH"
    data = b""

    icmp_packet = packet[20:] # Exctracting only the ICMP buffer

    icmp_pack_len = struct.calcsize(icmp_pack_str)
    packet_len = len(icmp_packet) - icmp_pack_len

    if packet_len > 0:
        icmp_data_str = f"{packet_len}s"
        data = struct.unpack(icmp_data_str, icmp_packet[icmp_pack_len:])[0]
    
    _type, code, checksum, _, _, dest_ip, \
        dest_port = struct.unpack(icmp_pack_str, icmp_packet[:icmp_pack_len])
    
    packet = ICMPPacket(_type, code, data,
                (socket.inet_ntoa(dest_ip), dest_port))
    packet.checksum = checksum
    return packet


def icmp_checksum(packet):
    """
    A checksum function that receives a raw ICMP packet, with zero in the checksum position,
    and calculates its checksum using the algorithm described at RFC1071: https://tools.ietf.org/html/rfc1071 
    """
    csum = 0
    countTo = (len(packet) / 2) * 2
    count = 0

    while count < countTo-1:
        thisVal = packet[count+1] * 256 + packet[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(packet):
        csum = csum + packet[len(packet) - 1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    checksum = ~csum
    checksum = checksum & 0xffff
    checksum = checksum >> 8 | (checksum << 8 & 0xff00)
    return checksum
