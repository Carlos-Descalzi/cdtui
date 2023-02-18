from typing import Any, Callable


class ListenerHandler:
    def __init__(self, source: Any):
        self._source = source
        self._listeners = []

    def add(self, listener: Callable) -> "ListenerHandler":
        self._listeners.append(listener)
        return self

    def remove(self, listener: Callable) -> "ListenerHandler":
        if listener in self._listeners:
            self._listeners.remove(listener)
        return self

    def __call__(self, *args, **kwargs):
        for listener in self._listeners:
            listener(self._source, *args, **kwargs)
