from abc import ABC, abstractmethod


class BaseQuery(ABC):

    @staticmethod
    @abstractmethod
    def load_commands(fp) -> list: ...

    @staticmethod
    @abstractmethod
    def update_lastlogin(user) -> str: ...

    @staticmethod
    @abstractmethod
    def finish_booking(event_id) -> str: ...
