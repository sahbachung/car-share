from abc import ABC, abstractmethod


class App(ABC):
    """Base type for a runnable App"""
    @abstractmethod
    def __init__(self, **kwargs): ...

    @abstractmethod
    def run(self, **kwargs): ...
