import platform

from abc import ABC, abstractmethod

from windows import WindowsNotification
from linux import LinuxNotification


class Notification(ABC):
    @classmethod
    def factory(cls):
        match platform.system():
            case "Windows":
                return WindowsNotification()
            case "Linux":
                return LinuxNotification()
            case _ as unsupported:
                raise NotImplementedError(unsupported)

    @abstractmethod
    def send(self, title: str, text: str) -> None:
        pass
