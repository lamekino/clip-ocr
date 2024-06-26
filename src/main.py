import sys
import subprocess

from pathlib import Path
from tempfile import NamedTemporaryFile
from clipocr.screenview import ScreenView
from clipocr.config import read_config


def main() -> int:
    config = read_config()  # TODO: catch exceptions, give meaningful errors

    text = ScreenView(config.tesseract_cmd).text()
    if text is None:
        return 1

    with NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as tmp:
        tmp.write(text)

    subprocess.run([str(config.editor), tmp.name])
    Path(tmp.name).unlink(missing_ok=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
