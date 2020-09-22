import argparse
import icmp
import select
import socket
import threading
import logging
import sys

logger = logging.getLogger()
TCP_BUFFER_SIZE = 2 ** 10
ICMP_BUFFER_SIZE = 65565


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(asctime)s - %(threadName)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def create_icmp_send_socket():
    """
    Creating an ICMP socket to send data over to the tunnel server
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except socket.error:
        raise
    return sock

def create_tcp_server_socket(listen_port):
    """
    Creating a TCP server socket to listen for incoming connections from the user on port `listen_port`. 
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", listen_port))
    except socket.error:
        raise
    return sock

class ClientSessionThread(threading.Thread):
    """
    A thread class to handle a user session. 
    This class handles wrapping TCP packets from the client in ICMP, and forwarding them to the tunnel server
    """

    def __init__(self, tunnel_server, sock, dest):
        threading.Thread.__init__(self)
        self.tunnel_server = tunnel_server
        self.dest = dest
        self.tcp_socket = sock
        self.icmp_socket = create_icmp_send_socket()
        self.sockets = [self.tcp_socket, self.icmp_socket]

    def run(self):
        """
        The thread entrypoint. Starting to listen on incoming data from the `tcp_server_socket`
        """
        logger.debug(f"Started a new thread trying to tunnel to {self.dest} through icmp'ing {self.tunnel_server}")
        while True:
            sread, _, _ = select.select(self.sockets, [], [])
            for sock in sread:
                if sock.proto == socket.IPPROTO_ICMP:
                    self.tunnel_to_client(sock)
                else:
                    self.client_to_tunnel(sock)

    def tunnel_to_client(self, sock):
        """
        Forwarding the ICMP packets received from the tunnel server to the client. 
        Unwraping the ICMP in the procedure.
        """
        logger.debug("Receiving ICMP packets from the tunnel server. Unwraping ICMP and forwarding TCP to the client")
        sdata = sock.recvfrom(ICMP_BUFFER_SIZE)
        packet = icmp.parse_icmp_buffer(sdata[0])
        if packet.type == icmp.ICMP_ECHO_REQUEST:
            # Not our packet
            return

        try:
            self.tcp_socket.send(packet.data)
        except ConnectionResetError:
            logger.warning("The client closed his TCP socket")
            self.exit_thread()

    def client_to_tunnel(self, sock):
        """
        Forwarding the TCP packets received from the client server to the tunnel server. 
        Wraping the TCP in ICMP during the procedure.
        """
        logger.debug("Receiving TCP packets from the client. Wraping them in ICMP and forwarding to the tunnel server")
        try:
            sdata = sock.recv(TCP_BUFFER_SIZE)
        except socket.error:
            logger.warning("The tunnel server closed its socket")
            sdata = ""

        # if no data the socket may be closed/timeout/EOF
        len_sdata = len(sdata)
        code = 0 if len_sdata > 0 else 1
        new_packet = icmp.ICMPPacket(icmp.ICMP_ECHO_REQUEST, code, sdata, self.dest)
        packet = new_packet.build_raw_icmp()
        self.icmp_socket.sendto(packet, (self.tunnel_server, 1))
        if code == 1:
            self.exit_thread()

    def exit_thread(self):
        """
        Exiting the thread and closing the sockets
        """
        logger.debug("Closing communication thread...")
        self.tcp_socket.close()
        self.icmp_socket.close()
        exit(0)


class Client:
    """
    A client class which handles the session threads
    """
    def __init__(self, tunnel_server, local_port, dest_host, dest_port):
        logger.info(f"Starting client. Tunnel Host: {tunnel_server}, Target Host: {dest_host}:{dest_port}...")
        self.tunnel_server = tunnel_server
        dest_host = socket.gethostbyname(dest_host)
        self.dest = (dest_host, dest_port)
        self.tcp_server_socket = create_tcp_server_socket(local_port)

    def run(self):
        """
        The main program loop of the client
        """
        while True:
            self.tcp_server_socket.listen(5)
            sock, _ = self.tcp_server_socket.accept()
            connection = ClientSessionThread(self.tunnel_server, sock, self.dest)
            connection.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tunnel-host",
                        help="Host on which the tunnel server is running", required=True)
    parser.add_argument("--listen-port", type=int,
                        help="Listen port for incoming TCP connections", required=True)
    parser.add_argument("--target-host",
                        help="Specifies the target's host with whom we'd like to create a TCP connection", 
                        type=str, required=True)
    parser.add_argument("--target-port", type=int,
                        help="Specifies the target's port with whom we'd like to create a TCP connection", required=True)

    args = parser.parse_args()

    client = Client(
        tunnel_server=args.tunnel_host, local_port=args.listen_port,
        dest_host=args.target_host, dest_port=args.target_port
    )

    client.run()
