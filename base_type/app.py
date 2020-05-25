from abc import ABC, abstractmethod


class App(ABC):

    @abstractmethod
    def __init__(self, **kwargs): ...

    @abstractmethod
    def run(self, **kwargs): ...
