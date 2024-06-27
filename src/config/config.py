import os
import platform as p

from dataclasses import dataclass
from typing import Optional, List, Set
from pathlib import Path


class PlatformException(Exception):
    pass


class ParseException(Exception):
    pass


class InvalidParamException(Exception):
    pass


class RequirementException(Exception):
    pass


ConfigKey = str


@dataclass
class Config:
    editor: str | Path

    tesseract_cmd: Optional[Path] = None
    enabledLangs: Optional[List[str]] = None  # TODO:

    def __contains__(self, param: ConfigKey) -> bool:
        return getattr(self, param, None) is not None


@dataclass
class Platform:
    config_path: Path
    defaults: Config
    required: Set[ConfigKey]

    @classmethod
    def windows(cls):
        userprofile = os.environ["USERPROFILE"]

        x64path = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        x86path = Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe")
        usepath = None

        if x64path.exists():
            usepath = x64path
        elif x86path.exists():
            usepath = x86path

        defaults = Config(
            editor="notepad.exe",
            tesseract_cmd=usepath,
        )

        return cls(
            config_path=Path(rf"{userprofile}\.config\clip-ocr"),
            defaults=defaults,
            required={},
        )

    @classmethod
    def linux(cls):
        home = os.environ["HOME"]

        defaults = Config(editor="gedit")

        return cls(
            config_path=Path(f"{home}/.config/clip-ocr"),
            defaults=defaults,
            required={},
        )

    @staticmethod
    def factory():
        match p.system():
            case "Linux":
                return Platform.linux()
            case "Windows":
                return Platform.windows()
            case _ as unsupported:
                raise PlatformException(unsupported)


class ConfigFile:
    def __init__(self, platform: Platform):
        self.fd = None
        self.config_file = platform.config_path

    def __enter__(self):
        try:
            self.fd = open(self.config_file)
        except FileNotFoundError:
            self.fd = open(os.devnull)

        return self.fd

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fd.close()


def read_config() -> Config:
    platform = Platform.factory()
    config = platform.defaults

    with ConfigFile(platform) as cfg:
        for num, line in enumerate(cfg.readlines()):
            setting, sep, param = line.partition("=")

            if not sep:
                raise ParseException(num)

            setting = setting.strip()
            param = param.strip()

            if not hasattr(Config, setting):
                raise InvalidParamException(setting)

            setattr(config, setting, param)

    for req in platform.required:
        if req not in config:
            if req not in platform.defaults:
                raise RequirementException(req)

            setattr(config, req, getattr(platform.defaults, req))

    return config
