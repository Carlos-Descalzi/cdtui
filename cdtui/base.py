from dataclasses import dataclass

COLORS = {
    "titledview.bg": "\u001b[48;5;241m",
    "titledview.fg": "\u001b[38;5;0m",
    "titledview.focused.bg": "\u001b[48;5;244m",
    "titledview.focused.fg": "\u001b[38;5;255m",
    "tabbedview.bg": "\u001b[48;5;241m",
    "tabbedview.fg": "\u001b[38;5;0m",
    "tabbedview.focused.bg": "\u001b[48;5;244m",
    "tabbedview.focused.fg": "\u001b[38;5;255m",
    "tabbedview.selected.bg": "\u001b[48;5;241m",
    "tabbedview.selected.fg": "\u001b[38;5;0m",
    "tabbedview.focused.selected.bg": "\u001b[48;5;244m",
    "tabbedview.focused.selected.fg": "\u001b[38;5;255m\u001b[1m",
    "textview.bg": "\u001b[48;5;236m",
    "textview.fg": "\u001b[38;5;255m",
    "filechooser.header.bg": "\u001b[48;5;241m",
    "filechooser.header.fg": "\u001b[38;5;255m\u001b[1m",
    "filechooser.footer.bg": "\u001b[48;5;236m",
    "filechooser.footer.fg": "\u001b[38;5;255m",
    "filechooser.bg": "\u001b[48;5;0m",
}


@dataclass
class Point:
    x: int = 0
    y: int = 0

    def __str__(self) -> str:
        return f"Point:{self.x},{self.y}"

    def copy(self):
        return Point(self.x, self.y)


@dataclass
class Dimension:
    width: int = 0
    height: int = 0

    def __str__(self):
        return f"Dimension:{self.width},{self.height}"

    def copy(self):
        return Dimension(self.width, self.height)


@dataclass
class Rect:
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    def __str__(self):
        return f"Rect:{self.x},{self.y},{self.width},{self.height}"

    @property
    def location(self):
        return Point(self.x, self.y)

    @property
    def dimension(self):
        return Dimension(self.width, self.height)

    def copy(self):
        return Rect(self.x, self.y, self.width, self.height)
