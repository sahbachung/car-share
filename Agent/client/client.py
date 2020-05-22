
# PACKET_HEADER_SIZE = 10
#
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((socket.gethostname(), 2999))
#
# while True:
#     full_msg = ""
#     msglen = 0
#     new_msg = True
#     while True:
#         msg = s.recv(16)
#         if len(msg)>0:
#             if new_msg:
#                 print(f"new message length: {msg[:PACKET_HEADER_SIZE]}")
#                 msglen = int(msg[:PACKET_HEADER_SIZE])
#                 new_msg = False
#             full_msg += msg.decode("utf-8")
#             if len(full_msg)-PACKET_HEADER_SIZE == msglen:
#                 print("full mesg received")
#                 print(full_msg[PACKET_HEADER_SIZE:])
#                 new_msg = True

import socket
import json

from base_type.packet import Request


def add_header(msg: bytes, h: int) -> bytes:
    return bytes(f"{len(msg):<{h}}", encoding="utf-8") + msg


class Client:

    def __init__(self, config=None):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with open(config) as conf:
            self.config = json.load(conf)
        self.connect()

    def connect(self):
        self.conn.connect((self.config["host"], self.config["port"]))
        print("Connection to {host} has been established!".format(**self.config))

    def login(self, user, password):
        print(f"logging in as {user}")
        self.conn.send(self.get_payload(
            Request.USER_LOGIN.get_payload(
                user=user,
                password=password,
                **self.config))
            )

    def get_payload(self, msg:dict) -> bytes:
        payload = bytes(json.dumps(msg), encoding="utf-8")
        payload = add_header(payload, self.config['packet_header_size'])
        return payload

    def await_response(self, server):
        payload = b""
        new = True
        buffer = self.config["packet_buffer_size"]
        header_size = self.config["packet_header_size"]
        length = 0
        while True:
            data = server.recv(buffer)
            if len(data) > 0:
                if new:
                    length = int(data[:header_size])
                    new = False
                    print(f"New Response packet\nLength: {length}")
                payload += data.decode("utf-8")
                if len(payload) - header_size >= length:
                    print("Response received")
                    payload = payload[header_size:]
                    return json.loads(payload, encoding="utf-8")


def main():
    client = Client("../../config.json")
    client.login("root", "passw0rd")


if __name__ == "__main__":
    main()
