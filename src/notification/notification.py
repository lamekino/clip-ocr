import platform

from .windows import WindowsNotification
from .linux import LinuxNotification


class Notification:
    @classmethod
    def factory(cls):
        match platform.system():
            case "Windows":
                return WindowsNotification()
            case "Linux":
                return LinuxNotification()
            case _ as unsupported:
                raise NotImplementedError(unsupported)
