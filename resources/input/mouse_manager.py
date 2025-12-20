from typing import Callable
import pyglet
from pyglet.window import mouse


class MouseManager(mouse.MouseStateHandler):
    def __init__(self):
        super().__init__()
        next(iter(pyglet.app.windows)).push_handlers(self)
        self.on_pressed_listeners: set[Callable] = set()
        self.on_dragging_listeners: set[Callable] = set()
        self.on_released_listeners: set[Callable] = set()
        self.on_motion_listeners: set[Callable] = set()
        self.on_scroll_listeners: set[Callable] = set()

    def _add_callback(self, callbacks_set, callback):
        if callback not in callbacks_set:
            callbacks_set.add(callback)

    def register_on_pressed_callback(self, callback: Callable[[int, int, int, int], None]):
        self._add_callback(self.on_pressed_listeners, callback)

    def register_on_dragging_callback(self, callback: Callable[[int, int, int, int, int, int], None]):
        self._add_callback(self.on_dragging_listeners, callback)

    def register_on_released_callback(self, callback: Callable[[int, int, int, int], None]):
        self._add_callback(self.on_released_listeners, callback)

    def register_on_motion_callback(self, callback: Callable[[int, int, int, int], None]):
        self._add_callback(self.on_motion_listeners, callback)

    def register_on_scroll_callback(self, callback: Callable[[int, int, int, int], None]):
        self._add_callback(self.on_scroll_listeners, callback)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.on_pressed_listeners:
            self._notify_listeners(self.on_pressed_listeners, x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.on_dragging_listeners:
            self._notify_listeners(self.on_dragging_listeners, x, y, dx, dy, buttons, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.on_released_listeners:
            self._notify_listeners(self.on_released_listeners, x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.on_motion_listeners:
            self._notify_listeners(self.on_motion_listeners, x, y, dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.on_scroll_listeners:
            self._notify_listeners(self.on_scroll_listeners, x, y, scroll_x, scroll_y)

    def _notify_listeners(self, listeners_set, *args):
        dead_listeners = []
        for listener in listeners_set:
            try:
                listener(*args)
            except (AttributeError, ReferenceError):
                dead_listeners.append(listener)
        if dead_listeners:
            for dead_listener in dead_listeners:
                listeners_set.remove(dead_listener)
