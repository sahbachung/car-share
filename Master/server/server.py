import socket
import json

from base_type.packet import Response


def add_header(msg: bytes, h: int) -> bytes:
    return bytes(f"{len(msg):<{h}}", encoding="utf-8") + msg


# PACKET_HEADER_SIZE = 10
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
# s.bind((socket.gethostname(), 2999))
# s.listen(5)
#
# while True:
#     clientsocket, address = s.accept()
#     print(f"Connection from {address} has been established!")
#     msg = "Welcome to the server!"
#     msg = f"{len(msg):<{PACKET_HEADER_SIZE}}" + msg
#     clientsocket.send(bytes(msg, "utf-8"))
class Server:

    def __init__(self, controller, config="../../config.json"):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with open(config) as conf:
            self.config = json.load(conf)
        self.conn.bind((self.config["host"], self.config["port"]))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def listen(self, backlog=5):
        print(f"Listening at {self.config['host']}:{self.config['port']}")
        self.conn.listen(backlog)
        while True:
            client_socket, address = self.conn.accept()
            print(f"Connection from {address} has been established!")
            req = self.await_request(client_socket)
            self.process_request(req)

    def await_request(self, client) -> dict:
        payload = b""
        new = True
        buffer = self.config["packet_buffer_size"]
        header_size = self.config["packet_header_size"]
        length = 0
        while True:
            data = client.recv(buffer)
            if len(data) > 0:
                if new:
                    length = int(data[:header_size])
                    new = False
                    print(f"New Request packet\nLength: {length}")
                payload += data.decode("utf-8")
                if len(payload) - header_size >= length:
                    print("Request received")
                    payload = payload[header_size:]
                    return json.loads(payload, encoding="utf-8")

    def process_request(self, req) -> Response:
        # TODO process req and generate a Response object
        ...

    def send_response(self, response: Response):
        payload = response.get_payload()
        payload = bytes(str(payload), encoding="utf-8")
        payload = add_header(payload, self.config["packet_header_size"])
