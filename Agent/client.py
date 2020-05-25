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


from base_type.packet import Request, Response, InvalidPacket


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

    def login(self, user, password) -> Response:
        print(f"Logging in as {user}")
        response = Request.USER_LOGIN.send(self, user=user, password=password)
        print(f"Response received {response}")
        return response

    def verify_user(self, user, car_id):
        print(f"Requesting access for car: {car_id}")
        response = Request.USER_VERIFY.send(self, user=user, car_id=car_id)
        print(f"Response received {response}")
        return response

    def return_car(self, user, car_id):
        print(f"Requesting to return car: {car_id}")
        response = Request.CAR_RETURN.send(self, username=user, car_id=car_id)
        return response

    def get_payload(self, msg: dict) -> bytes:
        payload = bytes(json.dumps(msg), encoding="utf-8")
        payload = add_header(payload, self.config['packet_header_size'])
        return payload

    def await_response(self):
        payload = b""
        data = b" "
        new = True
        buffer = self.config["packet_buffer_size"]
        header_size = self.config["packet_header_size"]
        msg = {}
        length = 0
        while data:
            data = self.conn.recv(buffer)
            if len(data) > 0:
                if new:
                    length = int(data[:header_size])
                    new = False
                    payload = data
                    continue
                payload += data
                if len(payload) - header_size == length:
                    try:
                        msg = json.loads(payload[header_size:], encoding="utf-8")
                    except json.decoder.JSONDecodeError:
                        raise InvalidPacket(payload)
                    finally:
                        new = not bool(payload) and bool(msg)
            if msg:
                return msg


def main():
    client = Client("../../config.json")
    client.login("root", "passw0rd")


if __name__ == "__main__":
    main()
