import sys
import pytesseract as ocr  # type: ignore

from pathlib import Path
from typing import Optional
from PIL import Image, ImageGrab, ImageTk

from tkinter import Tk, Canvas, Event, BOTH as TK_BOTH, NW as TK_NW

PImage = Image.Image


class NoTextException(Exception):
    pass


class ScreenView:
    def __init__(self, tesseract_cmd: Optional[Path]):
        self.root = Tk()

        self.start = (0, 0)
        self.finish = (0, 0)

        self.selection: Optional[object] = None
        self.screenshot = ImageGrab.grab()
        self.canvas = ScreenView.__config_window(self.root, self.screenshot)

        if tesseract_cmd is not None:
            ocr.pytesseract.tesseract_cmd = str(tesseract_cmd)
            print(ocr.pytesseract.tesseract_cmd)

        bindings = {
            "<Button-1>": self.__mouse_click,
            "<B1-Motion>": self.__mouse_hold,
            "<ButtonRelease>": lambda _: self.root.destroy(),
            "<Escape>": lambda _: sys.exit(1),  # FIXME: doesn't work
        }

        for button, action in bindings.items():
            self.canvas.bind(button, action)

    @staticmethod
    def __config_window(root: Tk, image: PImage) -> Canvas:
        background = ImageTk.PhotoImage(image)
        setattr(root, "image", background)

        root.attributes("-fullscreen", True)
        root.config(cursor="crosshair")

        width = root.winfo_width()
        height = root.winfo_height()

        canvas = Canvas(root, width=width, height=height)
        canvas.create_image(width, height, image=background, anchor=TK_NW)
        canvas.pack(fill=TK_BOTH, expand=True)

        return canvas

    def __mouse_click(self, event: Event) -> None:
        point = self.start = self.finish = (event.x, event.y)

        self.selection = self.canvas.create_rectangle(*point, *point, fill="")

    def __mouse_hold(self, event: Event) -> None:
        self.finish = (event.x, event.y)

        self.canvas.coords(self.selection,  # type: ignore
                           *self.start,
                           *self.finish)

    def text(self) -> Optional[str]:
        self.root.mainloop()

        x1, y1, x2, y2 = coords = (*self.start, *self.finish)

        if x1 > x2 and y1 > y2:
            coords = (x2, y2, x1, y1)

        text = ocr.image_to_string(self.screenshot.crop(coords))

        if not text:
            raise NoTextException

        return text
