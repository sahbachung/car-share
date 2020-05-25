from abc import ABC, abstractmethod


class BaseQuery(ABC):

    @staticmethod
    @abstractmethod
    def load_commands(fp) -> list: ...

