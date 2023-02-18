import subprocess
import sys
import unicodedata
from typing import Tuple

UNDERLINE = "\u001b[4m"
BOLD = "\u001b[1m"
REVERSE = "\u001b[7m"
RESET = "\u001b[0m"
CLRSCR = "\u001b[2J"
CURSOR_OFF = "\033[?25l"
CURSOR_ON = "\033[?25h"


class UiWriter:
    def __init__(self):
        self._buffer = ""

    def cursor_off(self) -> "UiWriter":
        self._buffer += CURSOR_OFF
        return self

    def cursor_on(self) -> "UiWriter":
        self._buffer += CURSOR_ON
        return self

    def clrscr(self) -> "UiWriter":
        self._buffer += CLRSCR
        return self

    def underline(self) -> "UiWriter":
        self._buffer += UNDERLINE
        return self

    def reverse(self) -> "UiWriter":
        self._buffer += REVERSE
        return self

    def bold(self) -> "UiWriter":
        self._buffer += BOLD
        return self

    def reset(self) -> "UiWriter":
        self._buffer += RESET
        return self

    def gotoxy(self, x: int, y: int) -> "UiWriter":
        self._buffer += f"\u001b[{y};{x}H"
        return self

    def write(self, string: str) -> "UiWriter":
        self._buffer += string
        return self

    def writefill(self, string: str, length: int, fillchar: str = " ") -> "UiWriter":
        str_len = _ansi_string_len(string)
        self._buffer += string + fillchar * (length - str_len)
        return self

    def fg(self, color: int) -> "UiWriter":
        self._buffer += f"\u001b[38;5;{color}m"
        return self

    def bg(self, color: int) -> "UiWriter":
        self._buffer += f"\u001b[48;5;{color}m"
        return self

    def put(self):
        try:
            sys.stdout.write(self._buffer)
            sys.stdout.flush()
        except Exception:
            pass

    def trunc(self, length: int) -> "UiWriter":
        while len(self) > length:
            self._buffer = self._buffer[0:-1]
        return self

    def __str__(self) -> str:
        return self._buffer

    def __len__(self) -> int:
        return _ansi_string_len(self._buffer)


def _ansi_string_len(string: str) -> int:
    sl = 0
    skip = False
    for c in string:
        if c == "\u001b":
            skip = True
        elif c in "mHJ" and skip:
            skip = False
        elif not skip:
            sl += 2 if unicodedata.east_asian_width(c) == "W" else 1
    return sl


def begin() -> UiWriter:
    return UiWriter()


def terminal_size() -> Tuple[int, int]:
    output = subprocess.check_output(["stty", "size"]).decode()
    return tuple(map(int, output.strip().split(" ")))


def cursor_on():
    subprocess.check_output(["tput", "cnorm"])


def cursor_off():
    subprocess.check_output(["tput", "civis"])
