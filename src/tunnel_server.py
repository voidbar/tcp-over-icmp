
import sys
import argparse
import icmp
import select
import socket
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)

TCP_BUFFER_SIZE = 2 ** 10
ICMP_BUFFER_SIZE = 65565

class Tunnel(object):
    def __init__(self):
        self.tcp_socket = None
        self.icmp_server_socket = self.create_icmp_server_socket()
        self.icmp_send_socket = self.create_icmp_send_socket()
        self.source, self.dest = None, None

    @staticmethod
    def create_icmp_server_socket():
        """
        Creating a socket for listening for ICMP packets from the client
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.bind(("0.0.0.0", 0))
        sock.setsockopt(socket.SOL_IP, socket.IP_HDRINCL, 1)
        return sock

    @staticmethod
    def create_icmp_send_socket():
        """
        Creating a socket for sending ICMP packets to the client
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        return sock

    @staticmethod
    def create_tcp_socket(dest):
        """
        Creating a socket for listening for sending TCP packets to the target
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect(dest)
        return sock

    def client_to_target(self):
        """
        Sending ICMP packets that were received from the client, to the server. Unwraping the ICMP and forwarding TCP to target
        """
        logger.info("Receiving ICMP packets from the client's server. Unwraping ICMP and forwarding TCP to the target")

        packet, addr = self.icmp_server_socket.recvfrom(ICMP_BUFFER_SIZE)
        try:
            packet = icmp.parse_tcp_packet(packet)
        except ValueError:
            return
        if packet.type == icmp.ICMP_ECHO_REPLY and packet.code == 0:
            logger.debug("Received our packet, Ignoring.")
            return

        self.source = addr[0]
        self.dest = packet.dest
        if packet.type == icmp.ICMP_ECHO_REQUEST and packet.code == 1:
            if self.tcp_socket in self.sockets:
                self.sockets.remove(self.tcp_socket)
            if self.tcp_socket:
                self.tcp_socket.close()
            self.tcp_socket = None
            return
            
        else:
            if not self.tcp_socket:
                logger.debug(f"Creating a new tcp socket to communicate with {self.dest}")
                self.tcp_socket = self.create_tcp_socket(self.dest)
                self.sockets.append(self.tcp_socket)
            self.tcp_socket.send(packet.data)

    def target_to_client(self, sock):
        """
        Receiving TCP packets from the target server. Wraping them in ICMP and forwarding them to the client
        """
        logger.debug("Receiving TCP packets from the target. Wraping them in ICMP and forwarding to the client server")
        try:
            sdata = sock.recv(TCP_BUFFER_SIZE)
        except OSError:
            return
        new_packet = icmp.ICMPPacket(icmp.ICMP_ECHO_REPLY, 0, 0, 0,
                                     sdata, self.source, self.dest)
        packet = new_packet.build_raw_icmp()
        self.icmp_send_socket.sendto(packet, (self.source, 0))

    def run(self):
        """
        Starting the tunnel which listens for ICMP packets from the client and forwards them to the target,
        And listening on TCP packets from the target to forward to the client
        """
        logger.info("Started listening from incoming ICMP packets...")
        self.sockets = [self.icmp_server_socket]
        while True:
            sread, _, _ = select.select(self.sockets, [], [])
            for sock in sread:
                if sock.proto == socket.IPPROTO_ICMP:
                    self.client_to_target()
                else:
                    self.target_to_client(sock)
    


if __name__ == "__main__":
    tunnel = Tunnel()
    tunnel.run()
