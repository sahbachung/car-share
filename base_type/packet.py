import datetime
import socket
from enum import Enum
import json


class Response(Enum):

    UNKNOWN_ERROR = 0
    LOGIN_ERROR = 0.1
    BOOKING_ERROR = 0.2
    RETURN_ERROR = 0.3
    LOGIN_SUCCESS = 1.1
    BOOKING_VERIFY = 1.2
    RETURN_SUCCESS = 1.3

    def send(self, client_socket: socket.socket, header_length):
        payload = self.get_payload(header_length)
        client_socket.send(payload)

    def get_payload(self, header_length, **kwargs) -> bytes:
        msg = {
            "response": self.value,
            "from": socket.gethostname(),
            "time": datetime.datetime.now().strftime(kwargs.get("date_format", "%A %d %B %Y(%H:%M:%S %f)"))
        }
        payload = json.dumps(msg).encode(encoding="utf-8")
        length = len(payload)
        header = f"{length:<{header_length}}"
        return bytes(header, encoding="utf-8") + payload

    def __str__(self) -> str:
        return f"< RESPONSE: {self.value} - {self.name} >"

    def __bool__(self):
        if self.value < 1:
            return False
        return True


class Request(Enum):
    INVALID = 0
    USER_LOGIN = 1
    USER_VERIFY = 2
    CAR_RETURN = 3

    def send(self, client, **kwargs) -> Response:
        """Sends the Request packet to the server and waits for a Response packet"""
        payload = self.get_payload(client.config, **kwargs)
        client.conn.send(payload)
        response = client.await_response()
        return Response(response["response"])

    def get_payload(self, config, **kwargs) -> bytes:
        assert kwargs.get("user", None) is not None
        msg = {
            "request": self.value,
            "from": socket.gethostname(),
            "time": datetime.datetime.now().strftime(config.get("date_format", "%A %d %B %Y(%H:%M:%S %f)")),
            "user": kwargs["user"]
        }
        header_length = config["packet_header_size"]
        if self is Request.USER_LOGIN:
            """Asks the server if the credentials are valid and if the user has booked the car"""
            assert kwargs.get("password", None) is not None
            msg["password"] = kwargs.get("password")
        elif self is Request.USER_VERIFY or self is Request.CAR_RETURN:
            assert kwargs.get("car_id", None) is not None
            msg["car_id"] = kwargs["car_id"]
        payload = json.dumps(msg).encode(encoding="utf-8")
        length = len(payload)
        header = f"{length:<{header_length}}"
        return bytes(header, encoding="utf-8") + payload

    def __str__(self) -> str:
        return f"< REQUEST: {self.value} - {self.name} >"

    def __bool__(self):
        if self is Request.INVALID:
            return False
        return True


class BasePacketException(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return f"BasePacketException({self.args})"


class EndOfPacketError(BasePacketException):
    def __init__(self, packet, header_size):
        self.packet = packet
        self.header_size = header_size

    def __str__(self):
        return f"A packet did not match its header length (header={self.header_size}, packet={self.packet})"


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
