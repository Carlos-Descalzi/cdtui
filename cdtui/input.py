from . import ansi, kbd
from .base import Rect
from .listener import ListenerHandler
from .view import View


class Input(View):
    def __init__(self, rect: Rect = None, disallowed_chars: str = ""):
        super().__init__(rect)
        self._on_enter = ListenerHandler(self)
        self._buffer = ""
        self._cursor_x = 0
        self._disallowed_chars = disallowed_chars

    def set_disallowed_chars(self, disallowed_chars: str):
        self._disallowed_chars = disallowed_chars or ""

    def get_disallowed_chars(self) -> str:
        return self._disallowed_chars

    disallowed_chars = property(get_disallowed_chars, set_disallowed_chars)

    @property
    def on_enter(self):
        return self._on_enter

    def on_key_press(self, input_key):

        if input_key == kbd.KEY_BACKSPACE:
            if self._cursor_x > 0:
                self._buffer = self._buffer[0 : len(self._buffer) - 1]
                self._cursor_x -= 1
                self.update()
        elif input_key == kbd.KEY_ENTER:
            self._on_enter(str(self._buffer))
        elif input_key < 127:
            char = chr(input_key)
            if char not in self._disallowed_chars:
                self._buffer += char
                self._cursor_x += 1
                self.update()

    def update(self):
        (ansi.begin().gotoxy(self._rect.x, self._rect.y).writefill(self._buffer, self._rect.width, "_")).put()
