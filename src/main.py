import sys
import subprocess

from pathlib import Path
from tempfile import NamedTemporaryFile

from clipocr.screenview import ScreenView
from clipocr.config import read_config

from notification.windows_notify import Notification


def main() -> int:
    notification = Notification.factory()
    config = read_config()

    text = ScreenView(config.tesseract_cmd).get_text()
    if not text:
        notification.send("Clip-OCR:", "No text found.")
        return 1

    with NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as tmp:
        tmp.write(text)

    notification.send("Clip-OCR copied text:", text.replace('\n', ' '))
    # subprocess.run([str(config.editor), tmp.name])

    Path(tmp.name).unlink(missing_ok=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
