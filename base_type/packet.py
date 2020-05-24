import datetime
import socket
from enum import Enum
import json


class Request(Enum):
    USER_LOGIN = 0
    USER_VERIFY = 1
    CAR_RETURN = 2

    def send(self, client, **kwargs):
        payload = self.get_payload(client.config, **kwargs)
        client.conn.send(payload)
        response = client.await_response()
        return Response(response["response"])

    def get_payload(self, config, **kwargs) -> bytes:
        msg = {
            "request": self.value,
            "from": socket.gethostname(),
            "time": datetime.datetime.now().strftime(config.get("date_format"))
        }
        header_length = config["packet_header_size"]
        if self is Request.USER_LOGIN:
            """Asks the server if the credentials are valid and if the user has booked the car"""
            assert all((kwargs.get(kwarg) for kwarg in ["user", "password"]))
            msg["user"] = kwargs.get("user")
            msg["password"] = kwargs.get("password")
        elif self is Request.USER_VERIFY or self is Request.CAR_RETURN:
            assert all((kwargs.get(kwarg) for kwarg in ["user", "car_id"]))
            msg["user"] = kwargs.get("user")
            msg["car_id"] = kwargs.get("car_id")
        payload = json.dumps(msg).encode(encoding="utf-8")
        length = len(payload)
        header = f"{length:<{header_length}}"
        return bytes(header, encoding="utf-8") + payload

    def __str__(self) -> str:
        return f"< REQUEST: {self.value} - {self.name} >"


class Response(Enum):

    UNKNOWN_ERROR = 0
    LOGIN_ERROR = 0.1
    BOOKING_ERROR = 0.2
    LOGIN_SUCCESS = 1.1
    BOOKING_SUCCESS = 1.2

    def send(self, client_socket: socket.socket, header_length):
        payload = self.get_payload(header_length)
        client_socket.send(payload)

    def get_payload(self, header_length, **kwargs) -> bytes:
        msg = {
            "response": self.value,
            "from": socket.gethostname(),
            "time": datetime.datetime.now().strftime(kwargs.get("date_format"))
        }
        payload = json.dumps(msg).encode(encoding="utf-8")
        length = len(payload)
        header = f"{length:<{header_length}}"
        return bytes(header, encoding="utf-8") + payload

    def __str__(self) -> str:
        return f"< RESPONSE: {self.value} - {self.name} >"


class BasePacketException(Exception):
    def __init__(self, *args):
        pass


class EndOfPacketError(BasePacketException):
    def __init__(self, packet, header_size):
        self.packet = packet
        self.header_size = header_size

    def __str__(self):
        return f"A packet didn't match its header length (header={self.header_size}, packet={self.packet})"


class EmptyPacket(BasePacketException):
    def __init__(self, host):
        self.host = host

    def __str__(self):
        return f"Remote machine ({self.host}) sent an empty packet"


class InvalidPacket(BasePacketException):
    def __init__(self, packet:bytes):
        self.packet = packet

    def __str__(self):
        return f"Could not load {self.packet}"
