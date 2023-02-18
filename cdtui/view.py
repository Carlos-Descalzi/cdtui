
from . import kbd
from .base import COLORS, Rect
import logging 

_logger = logging.getLogger(__name__)


class View:
    def __init__(self, rect: Rect = None):
        self._focused = False
        self._rect = rect or Rect()
        self._dirty = True
        self._application = None
        self._visible = True
        self._focusable = True
        self._color_key_prefix = self.__class__.__name__.lower()

    def set_application(self, application):
        self._application = application

    def get_application(self):
        return self._application

    application = property(get_application, set_application)

    def set_visible(self, visible: bool):
        self._visible = visible

    def get_visible(self) -> bool:
        return self._visible

    visible = property(get_visible, set_visible)

    def set_rect(self, rect: Rect):
        old_rect = self._rect
        self._rect = rect
        if old_rect != rect:
            self._dirty = True

    def get_rect(self) -> Rect:
        return self._rect

    rect = property(get_rect, set_rect)

    def set_focused(self, focused: bool):
        old_focused = self._focused
        self._focused = focused
        if old_focused != focused:
            self.queue_update()

    def get_focused(self) -> bool:
        return self._focused

    focused = property(get_focused, set_focused)

    def set_focusable(self, focusable: bool):
        self._focusable = focusable

    def get_focusable(self) -> bool:
        return self._focusable

    focusable = property(get_focusable, set_focusable)

    def set_color_key_prefix(self, color_key_prefix: str):
        self._color_key_prefix = color_key_prefix

    def get_color_key_prefix(self) -> str:
        return self._color_key_prefix

    color_key_prefix = property(get_color_key_prefix, set_color_key_prefix)

    def get_color_key(self, color) -> str:
        return self._color_key_prefix + (".focused" if self.focused else "") + "." + color

    def get_color(self, key) -> str:
        return COLORS.get(self.get_color_key(key), "")

    def contains(self, child) -> bool:
        return False

    def on_key_press(self, key):
        pass

    def update(self):
        pass

    def queue_update(self):
        if self._application and self.visible:
            self._application.queue_update(self)
