import sys
import subprocess

from pathlib import Path
from tempfile import NamedTemporaryFile

# TODO: namespace these to clipocr.<module>
from config import read_config
from notification import Notification
from screenview import ScreenView


def main() -> int:
    notification = Notification.factory()
    config = read_config()

    text = ScreenView(config.tesseract_cmd).get_text()
    if not text:
        notification.send("Clip-OCR:", "No text found.")
        return 1

    with NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as tmp:
        tmp.write(text)

    # subprocess.run([str(config.editor), tmp.name])
    # need need to get an event handle for the click. powershell seems like a
    # pain. but i think that we can make a simple function that sends a signal
    # to this one and then opens the text from the screenview
    notification.send("Clip-OCR copied text:", text.replace('\n', ' '))

    Path(tmp.name).unlink(missing_ok=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
