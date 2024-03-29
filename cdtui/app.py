import atexit
import fcntl
import logging
import os
import sys
import termios
import time
import tty

from . import ansi, kbd

_logger = logging.getLogger(__name__)

class KeyHandler:
    def __init__(self, handler, valid_on_popup):
        self.handler = handler
        self.valid_on_popup = valid_on_popup

class PauseTermSettingsHandler:

    def __init__(self, app):
        self._app = app

    def __enter__(self):
        self._app._restore_term()

    def __exit__(self, *_, **__):
        self._app._init_term()

class Application:
    def __init__(self):
        self._components = []
        self._focused_index = 0
        self._active_popup = None
        self._popup_closeable = True
        self._active = True
        self._queue = set()
        self._key_handlers = {}
        self._term_attrs = None

    def add_component(self, component):
        component.set_application(self)
        self._components.append(component)

    def remove_component(self, component):
        self._components.remove(component)
        component.application = None
        if self._focused_index >= len(self._components):
            self._cycle_focus()

    def _init_term(self):
        self._term_attrs = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin)
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

    def _restore_term(self):
        ansi.begin().clrscr().cursor_on().put()
        if self._term_attrs:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._term_attrs)

    def pause_app(self) -> PauseTermSettingsHandler:
        return PauseTermSettingsHandler(self)

    def main_loop(self):

        self._init_term()

        atexit.register(self._restore_term)

        self.refresh()

        while self._active:
            self.empty_queue()
            self._check_keyboard()
            time.sleep(0.01)

        self._on_finish()

    def refresh(self):
        ansi.begin().clrscr().cursor_off().put()
        self._update_view()

    def _on_finish(self):
        """
        Placeholder for any release of resources
        """
        pass

    def empty_queue(self):
        queue = self._queue
        self._queue = set()
        try:
            for view in queue:
                if self._active_popup:
                    if self._is_in_popup(view):
                        view.update()
                else:
                    view.update()
        except Exception:
            _logger.exception()

    def _is_in_popup(self, view):
        return self._active_popup and (self._active_popup == view or self._active_popup.contains(view))

    def queue_update(self, view):
        self._queue.add(view)

    def set_key_handler(self, keystroke, handler, valid_on_popup=True):
        self._key_handlers[keystroke] = KeyHandler(handler, valid_on_popup)

    def unset_key_handler(self, keystroke):
        self._key_handlers.pop(keystroke)

    def _check_keyboard(self):
        read = sys.stdin.read(3)

        if len(read) > 0:
            keystroke = kbd.keystroke_from_str(read)

            if keystroke == kbd.KEY_ESC:
                self._handle_exit()
            elif keystroke == kbd.KEY_TAB:
                self._cycle_focus()
            elif keystroke == kbd.KEY_SHIFT_TAB:
                self._cycle_focus_back()
            else:
                handler = self._key_handlers.get(keystroke)
                _logger.debug(f"Key handler for keystroke {keystroke}: {handler}")

                if handler and (handler.valid_on_popup or not self._active_popup):
                    handler.handler(self)
                else:
                    self._send_key_event(keystroke)

    def _handle_exit(self):
        if self._active_popup:
            self.close_popup()
        else:
            self._active = False

    def _cycle_focus(self):
        if self._active_popup:
            self._active_popup.set_focused(True)

        if self._components:
            active = self._components[self._focused_index]
            active.set_focused(False)
            while True:
                self._focused_index += 1
                if self._focused_index >= len(self._components):
                    self._focused_index = 0
                if self._components[self._focused_index].focusable:
                    break
            active = self._components[self._focused_index]
            active.set_focused(True)

    def _cycle_focus_back(self):
        if self._active_popup:
            self._active_popup.set_focused(True)

        if self._components:
            active = self._components[self._focused_index]
            active.set_focused(False)
            while True:
                self._focused_index -= 1
                if self._focused_index < 0:
                    self._focused_index = len(self._components) - 1
                if self._components[self._focused_index].focusable:
                    break
            active = self._components[self._focused_index]
            active.set_focused(True)

    def set_focused_view(self, view):
        active = self._components[self._focused_index]
        active.set_focused(False)

        self._focused_index = self._components.index(view)
        view.set_focused(True)

    def _send_key_event(self, input_key):
        if self._active_popup:
            self._active_popup.on_key_press(input_key)
        else:
            if self._components:
                self._components[self._focused_index].on_key_press(input_key)

    def _update_view(self):
        if self._active_popup:
            self._active_popup.update()
        else:
            for component in self._components:
                component.update()

    def open_popup(self, view, closeable=True):
        max_height, max_width = ansi.terminal_size()
        view.set_application(self)
        view._rect.x = int((max_width - view._rect.width) / 2)
        view._rect.y = int((max_height - view._rect.height) / 2)
        self._active_popup = view
        self._active_popup.update()
        self._popup_closeable = closeable

    def close_popup(self):
        if self._active_popup:
            if self._popup_closeable:
                self._active_popup.set_application(None)
                self._active_popup = None
                ansi.begin().clrscr().put()
                self._update_view()
