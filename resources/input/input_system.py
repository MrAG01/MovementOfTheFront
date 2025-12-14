from weakref import WeakSet, ref, WeakMethod
from typing import Callable, Optional

import arcade
from pyglet.window import key
import pyglet


class InputSystem:
    _MODIFIERS = [key.MOD_SHIFT,
                  key.MOD_ALT,
                  key.MOD_CTRL,
                  key.MOD_COMMAND]

    def __init__(self):
        self.keyboard_handler = key.KeyStateHandler()
        next(iter(pyglet.app.windows)).push_handlers(self.keyboard_handler)

        self.mouse_hotkeys: dict[tuple[int, int], list[str]] = {}
        self.hotkeys: dict[tuple[int, int], list[str]] = {}

        self.on_pressed_listeners: dict[str, WeakSet[Callable]] = {}
        self.on_holding_listeners: dict[str, WeakSet[Callable]] = {}
        self.on_released_listeners: dict[str, WeakSet[Callable]] = {}

        self._last_frame_pressed = set()

    def _notify_listeners(self, name, listeners_dict):
        if name in listeners_dict:
            for callback in listeners_dict:
                callback()

    def _register_in(self, name, listeners_dict, callback):
        if name in listeners_dict:
            listeners_dict[name].add(callback)
        else:
            listeners_dict[name] = WeakSet([callback])

    def register_callback(self,
                          name,
                          on_pressed_callback: Callable,
                          on_holding_callback: Optional[Callable] = None,
                          on_released_callback: Optional[Callable] = None):
        if on_pressed_callback:
            self._register_in(name, self.on_pressed_listeners, on_pressed_callback)
        if on_holding_callback:
            self._register_in(name, self.on_holding_listeners, on_holding_callback)
        if on_released_callback:
            self._register_in(name, self.on_released_listeners, on_released_callback)

    def _get_pressed_modifiers(self):
        kh = self.keyboard_handler

    def update(self):
        current_pressed = set()
        for key, pressed in self.keyboard_handler.data.items():
            if pressed:
                current_pressed.add(key)
                if key not in self._last_frame_pressed:
                    if key in self.hotkeys:
                        for name in self.hotkeys[key]:
                            self._notify_listeners(name, self.on_pressed_listeners)

        self._last_frame_pressed = current_pressed
