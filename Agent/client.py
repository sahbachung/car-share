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

import json
import socket


from base_type.packet import Request, EndOfPacketError, Response


def add_header(msg: bytes, h: int) -> bytes:
    return bytes(f"{len(msg):<{h}}", encoding="utf-8") + msg


class Client:

    def __init__(self, config):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.config = config

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def connect(self):
        try:
            self.conn.connect((self.config["host"], self.config["port"]))
        except ConnectionRefusedError:
            exit(print(Response(0)))
        print(f"Connection to {self.config['host']} has been established!")

    def login(self, user, password):
        print(f"Logging in as {user}")
        response = Request.USER_LOGIN.send(self, user=user, password=password)

    def get_payload(self, msg: dict) -> bytes:
        payload = bytes(json.dumps(msg), encoding="utf-8")
        payload = add_header(payload, self.config['packet_header_size'])
        return payload

    def await_response(self):
        payload = b""
        new = True
        buffer = self.config["packet_buffer_size"]
        header_size = self.config["packet_header_size"]
        length = 0
        while True:
            data = self.conn.recv(buffer)
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
            else:
                raise EndOfPacketError(payload, length)


def main():
    client = Client("../../config.json")
    client.login("root", "passw0rd")


if __name__ == "__main__":
    main()
