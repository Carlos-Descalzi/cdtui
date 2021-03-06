from . import ansi, kbd
from .base import Rect, COLORS
import time
import sys
import tty
import logging


class View:
    def __init__(self, rect=None):
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

    def set_visible(self, visible):
        self._visible = visible

    def get_visible(self):
        return self._visible

    visible = property(get_visible, set_visible)

    def set_rect(self, rect):
        old_rect = self._rect
        self._rect = rect
        if old_rect != rect:
            self._dirty = True

    def get_rect(self):
        return self._rect

    rect = property(get_rect, set_rect)

    def set_focused(self, focused):
        old_focused = self._focused
        self._focused = focused
        if old_focused != focused:
            self.queue_update()

    def get_focused(self):
        return self._focused

    focused = property(get_focused, set_focused)

    def set_focusable(self, focusable):
        self._focusable = focusable

    def get_focusable(self):
        return self._focusable

    focusable = property(get_focusable, set_focusable)

    def set_color_key_prefix(self, color_key_prefix):
        self._color_key_prefix = color_key_prefix

    def get_color_key_prefix(self):
        return self._color_key_prefix

    color_key_prefix = property(get_color_key_prefix, set_color_key_prefix)

    def get_color_key(self, color):
        return (
            self._color_key_prefix + (".focused" if self.focused else "") + "." + color
        )

    def get_color(self, key):
        return COLORS.get(self.get_color_key(key), "")

    def contains(self, child):
        return False

    def on_key_press(self, key):
        pass

    def update(self):
        pass

    def queue_update(self):
        if self._application and self.visible:
            self._application.queue_update(self)
