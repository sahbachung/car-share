from enum import Enum
import socket
import datetime


class Request(Enum):

    USER_LOGIN = 0
    USER_VERIFY = 1
    CAR_RETURN = 2

    def get_payload(self, **kwargs) -> dict:
        msg = {
            "request": str(self),
            "from": socket.gethostname(),
            "time": datetime.datetime.now().strftime(kwargs.get("date_format"))
        }
        if self == Request.USER_LOGIN:
            """Asks the server if the credentials are valid and if the user has booked the car"""
            assert all((kwargs.get(i) for i in ["user", "password"]))
            msg["user"] = kwargs.get("user")
            msg["password"] = kwargs.get("password")
        elif self == Request.USER_VERIFY:...
        #   TODO implement verifying that the user has permission to use the car
        elif self == Request.CAR_RETURN:...
        #   TODO implement telling the server that a car is being returned
        return msg

    def __str__(self) -> str:
        return f"< REQUEST: {self.value} - {self.name} >"


class Response(Enum):

    SERVER_ERROR = 0.0
    LOGIN_ERROR = 0.1
    BOOKING_ERROR = 0.2
    LOGIN_SUCCESS = 1.1
    BOOKING_SUCCESS = 1.2

    def get_payload(self, **kwargs) -> dict:
        msg = {
            "response": str(self),
            "from": socket.gethostname(),
            "time": datetime.datetime.now().strftime(kwargs.get("date_format"))
        }
        return msg

    def __str__(self) -> str:
        return f"< RESPONSE: {self.value} - {self.name} >"
