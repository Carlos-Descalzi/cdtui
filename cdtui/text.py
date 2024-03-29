from . import ansi, kbd
from .base import Rect
from .view import View


class TextView(View):
    """
    A text viewer
    """

    def __init__(self, rect: Rect = None, text: str = ""):
        super().__init__(rect)
        self._text = self._sanitize(text)
        self._scroll_x = 0
        self._scroll_y = 0

    def set_text(self, text: str):
        self._scroll_x = 0
        self._scroll_y = 0
        self._text = self._sanitize(text)
        self.queue_update()

    def get_text(self) -> str:
        return "\n".join(self._text)

    text = property(get_text, set_text)

    def _sanitize(self, text):
        return list(map(self._sanitize_line, text.split("\n")))

    def _sanitize_line(self, text_line: str) -> str:
        return (
            text_line.replace("\r", "")
            .replace("\n", "")
            .replace(ansi.RESET, ansi.RESET + self.get_color("bg") + self.get_color("fg"))
        )

    def update(self):
        height = self._rect.height
        width = self._rect.width

        chunk = self._text[self._scroll_y : self._scroll_y + height]
        chunk = [l[self._scroll_x : self._scroll_x + width] for l in chunk]

        buff = ansi.begin()
        for i, line in enumerate(chunk):
            buff.write(self.get_color("bg")).write(self.get_color("fg")).gotoxy(
                self._rect.x, self._rect.y + i
            ).writefill(line, self._rect.width).reset()

        buff.write(self.get_color("bg"))
        i += 1
        while i < self._rect.height:
            buff.gotoxy(self._rect.x, self._rect.y + i).writefill("", self._rect.width)
            i += 1
        buff.reset().put()

    def on_key_press(self, input_key):
        if input_key == kbd.KEY_DOWN:
            self._scroll_down()
        elif input_key == kbd.KEY_UP:
            self._scroll_up()
        elif input_key == kbd.KEY_LEFT:
            self._scroll_left()
        elif input_key == kbd.KEY_RIGHT:
            self._scroll_right()
        elif input_key == kbd.KEY_PGUP:
            self._page_up()
        elif input_key == kbd.KEY_PGDN:
            self._page_down()
        elif input_key == kbd.KEY_HOME:
            self._home()

    def _home(self):
        self._scroll_y = 0
        self._scroll_x = 0
        self.queue_update()

    def _page_down(self):
        self._scroll_y += self._rect.height
        if self._scroll_y + self._rect.height >= len(self._text):
            self._scroll_y = len(self._text) - self._rect.height - 1
        self.queue_update()

    def _page_up(self):
        self._scroll_y -= self._rect.height
        if self._scroll_y < 0:
            self._scroll_y = 0
        self.queue_update()

    def _scroll_down(self):
        if self._scroll_y + self._rect.height < len(self._text) - 1:
            self._scroll_y += 1
            self.queue_update()

    def _scroll_up(self):
        if self._scroll_y > 0:
            self._scroll_y -= 1
            self.queue_update()

    def _scroll_right(self):
        self._scroll_x += 1
        self.queue_update()

    def _scroll_left(self):
        if self._scroll_x > 0:
            self._scroll_x -= 1
            self.queue_update()
