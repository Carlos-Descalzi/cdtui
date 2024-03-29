from . import ansi, kbd
from .base import Rect
from .view import View


class TitledView(View):
    """
    A container for a single view with title
    """

    def __init__(self, rect: Rect = None, title: str = "", inner: View = None):
        super().__init__(rect)
        self._title = title
        self._inner = inner
        self._update_inner()

    def on_key_press(self, key):
        if self._inner:
            self._inner.on_key_press(key)

    def set_focused(self, focused):
        super().set_focused(focused)
        if self._inner:
            self._inner.set_focused(focused)

    def set_application(self, application):
        super().set_application(application)
        if self._inner:
            self._inner.set_application(application)

    def set_rect(self, rect):
        self._update_inner()
        super().set_rect(rect)

    def contains(self, child):
        return self._inner == child

    def set_title(self, title: str):
        self._title = title
        self.queue_update()

    def get_title(self) -> str:
        return self._title

    title = property(get_title, set_title)

    def _update_inner(self):
        if self._inner:
            inner_rect = self._rect.copy()
            inner_rect.y += 1
            inner_rect.height -= 1
            self._inner.set_rect(inner_rect)

    def update(self):
        buff = ansi.begin().gotoxy(self._rect.x, self._rect.y)

        (
            buff.write(self.get_color("bg"))
            .write(self.get_color("fg"))
            .writefill(self._title, self._rect.width)
            .reset()
        ).put()

        if self._inner:
            self._inner.update()
