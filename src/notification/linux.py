from .sender import Sender


class LinuxNotification(Sender):
    def __init__(self):
        raise NotImplementedError(
            "Linux notifications have not been implemented")

    def send(self, title: str, text: str) -> None:
        raise NotImplementedError()
