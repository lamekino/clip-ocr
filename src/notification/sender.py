from abc import ABC, abstractmethod


class Sender(ABC):
    @abstractmethod
    def send(self, title: str, text: str) -> None:
        pass
