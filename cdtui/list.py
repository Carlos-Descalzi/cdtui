import logging
import traceback
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from . import ansi, kbd
from .listener import ListenerHandler
from .view import View

T = TypeVar("T")


class ListModel(ABC, Generic[T]):
    def __init__(self):
        self._on_list_changed = ListenerHandler(self)

    @property
    def on_list_changed(self) -> ListenerHandler:
        return self._on_list_changed

    def notify_list_changed(self):
        self._on_list_changed()

    @abstractmethod
    def get_item_count(self) -> int:
        pass

    @abstractmethod
    def get_item(self, index: int) -> Optional[T]:
        pass


class DefaultListModel(ListModel[T]):
    def __init__(self, items=[]):
        super().__init__()
        self._items = items

    def get_item_count(self) -> int:
        return len(self._items)

    def get_item(self, index: int) -> T:
        return self._items[index]

    def get_items(self) -> List[T]:
        return self._items

    def set_items(self, items: Optional[List[T]]):
        self._items = items or []
        self.notify_list_changed()

    items = property(get_items, set_items)


class ListView(View):
    def __init__(self, rect=None, model=None, selectable=False):
        super().__init__(rect)
        self._model = None
        self._scroll_y = 0
        self._selectable = selectable
        self._current_index = -1
        self._selected_index = -1
        self._on_select = ListenerHandler(self)
        self.set_model(model)
        self._item_renderer = self._default_render

    def set_selectable(self, selectable: bool):
        self._selectable = selectable

    def get_selectable(self) -> bool:
        return self._selectable

    selectable = property(get_selectable, set_selectable)

    @property
    def on_select(self) -> ListenerHandler:
        return self._on_select

    def set_selected_index(self, index: int):
        self._selected_index = index
        if index != -1:
            self._notify_selected(index)

    def get_selected_index(self) -> int:
        return self._selected_index

    selected_index = property(get_selected_index, set_selected_index)

    @property
    def current_item(self):
        return self._model.get_item(self._current_index) if self._current_index != -1 else None

    def set_model(self, model):
        if self._model:
            self._model.on_list_changed.remove(self._model_changed)

        self._model = model

        if self._model:
            self._model.on_list_changed.add(self._model_changed)

    def _model_changed(self, *_):
        self._current_index = 0 if self._model.get_item_count() > 0 else -1
        self._scroll_y = 0
        # if self._current_index >= self._model.get_item_count():
        #    if self._model.get_item_count() > 0:
        #        self._current_index = self._model.get_item_count() -1
        #        self._scroll_y = max(0, self._current_index-1)
        #    else:
        #        self._current_index = -1
        #        self._scroll_y = 0

        self.queue_update()

    def get_model(self):
        return self._model

    model = property(get_model, set_model)

    def set_item_renderer(self, item_renderer):
        if item_renderer is None:
            self._item_renderer = self._default_render
        else:
            self._item_renderer = item_renderer
        self.queue_update()

    def get_item_renderer(self):
        return self._item_renderer

    item_renderer = property(get_item_renderer, set_item_renderer)

    def _default_render(self, view, item):
        return str(item) if item else ""

    def render_item(self, item, current, selected):
        str_value = self._item_renderer(self, item)
        if current:
            return str(ansi.begin().underline().write(str_value).reset())
        return str_value

    def update(self):
        try:
            max_items = self._rect.height
            last_item = self._model.get_item_count() - 1

            from_index = self._scroll_y
            to_index = min(self._scroll_y + max_items - 1, last_item)

            current_index = self._current_index - self._scroll_y if self._current_index != -1 else -1
            selected_index = (self._selected_index - self._scroll_y) if self._selected_index != -1 else -1
            for i in range(from_index, to_index + 1):
                item = self._model.get_item(i)
                item_index = i - self._scroll_y

                current = item_index == current_index
                selected = self._selectable and item_index == selected_index

                text = self.render_item(item, current, selected)
                (
                    ansi.begin()
                    .gotoxy(self._rect.x, self._rect.y + i - self._scroll_y)
                    .writefill(text, self._rect.width)
                ).put()

            last_y = self._rect.y + (to_index + 1 - from_index)
            max_y = self._rect.y + self._rect.height - 1

            ui_buff = ansi.begin()
            while last_y <= max_y:
                ui_buff.gotoxy(self._rect.x, last_y).writefill("", self._rect.width)
                last_y += 1
            ui_buff.put()
        except Exception:
            logging.exception("Exception on list")

    def on_key_press(self, key):
        try:
            # item_count = self._model.get_item_count()
            if key == kbd.KEY_UP:
                self._scroll_up()
            elif key == kbd.KEY_DOWN:
                self._scroll_down()
            elif key == kbd.KEY_PGDN:
                self._page_down()
            elif key == kbd.KEY_PGUP:
                self._page_up()
            elif key == kbd.KEY_HOME:
                self._go_home()
            elif key == kbd.KEY_ENTER:
                if self._selectable:
                    self._select(self._current_index)
        except Exception:
            logging.exception("Exception on key handler")

    def _scroll_up(self):
        # item_count = self._model.get_item_count()
        if self._current_index > 0:
            self._current_index -= 1
            if self._current_index - self._scroll_y < 0:
                self._scroll_y -= 1
            self.queue_update()
        elif self._scroll_y > 0:
            self._scroll_y -= 1
            self.queue_update()

    def _scroll_down(self):
        item_count = self._model.get_item_count()
        if self._current_index < item_count - 1:
            self._current_index += 1
            if self._current_index - self._scroll_y >= self._rect.height:
                self._scroll_y += 1
            self.queue_update()

    def _page_down(self):
        item_count = self._model.get_item_count()
        self._scroll_y += self._rect.height
        if self._scroll_y + self._rect.height > item_count:
            self._scroll_y = max(0, item_count - self._rect.height)
        self._current_index = self._scroll_y
        self.queue_update()

    def _page_up(self):
        self._scroll_y -= self._rect.height
        if self._scroll_y < 0:
            self._scroll_y = 0
        self._current_index = self._scroll_y
        self.queue_update()

    def _go_home(self):
        self._current_index = 0
        self._scroll_y = 0
        self.queue_update()

    def _select(self, index):
        self._selected_index = index
        self._notify_selected(index)
        self.queue_update()

    def get_selected_item(self):
        if self._selected_index != -1:
            return self._model.get_item(self._selected_index)

    def _notify_selected(self, index):
        item = self._model.get_item(index) if index != -1 else None
        self._on_select(item)
