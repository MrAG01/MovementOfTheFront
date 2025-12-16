from typing import Callable, Optional
from pyglet.window import key
import pyglet
from configs.config_manager import ConfigManager
from resources.input.keyboard_manager_config import KeyboardManagerConfig


class KeyboardManager(key.KeyStateHandler):
    _MODIFIERS = [key.LSHIFT, key.RSHIFT,
                  key.LALT, key.RALT,
                  key.LCTRL, key.RCTRL,
                  key.LCOMMAND, key.RCOMMAND]

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        next(iter(pyglet.app.windows)).push_handlers(self)
        self.config = config_manager.register_config("keyboard_manager_config", KeyboardManagerConfig)

        self.on_pressed_listeners: dict[str, set[Callable]] = {}
        self.on_holding_listeners: dict[str, set[Callable]] = {}
        self.on_released_listeners: dict[str, set[Callable]] = {}

        self._last_frame_pressed = set()

        self._is_dirty = True
        self._holding_now = 0

    def on_key_press(self, key, *args):
        super().on_key_press(key, *args)
        self._is_dirty = True
        self._holding_now += 1

    def on_key_release(self, key, *args):
        super().on_key_release(key, *args)
        self._is_dirty = True
        self._holding_now -= 1

    def _notify_listeners(self, names, listeners_dict):
        for name in names:
            if name in listeners_dict:
                for callback in listeners_dict[name]:
                    try:
                        callback()
                    except (ReferenceError, AttributeError):
                        listeners_dict[name].remove(callback)

    def _register_in(self, name, listeners_dict, callback):
        if name in listeners_dict:
            listeners_dict[name].add(callback)
        else:
            listeners_dict[name] = {callback}

    def bind_key(self, key, modifier, name):
        dict_key = (key, modifier)
        if dict_key in self.config.hotkeys:
            self.config.hotkeys[dict_key].append(name)
        else:
            self.config.hotkeys[dict_key] = [name]

    def register_callback(self,
                          name,
                          on_pressed_callback: Optional[Callable] = None,
                          on_holding_callback: Optional[Callable] = None,
                          on_released_callback: Optional[Callable] = None):
        if not (on_pressed_callback or on_holding_callback or on_released_callback):
            return

        if on_pressed_callback:
            self._register_in(name, self.on_pressed_listeners, on_pressed_callback)
        if on_holding_callback:
            self._register_in(name, self.on_holding_listeners, on_holding_callback)
        if on_released_callback:
            self._register_in(name, self.on_released_listeners, on_released_callback)

    def _get_pressed_modifiers(self):
        modifiers = 0
        for mod in KeyboardManager._MODIFIERS:
            if self[mod]:
                modifiers |= mod
        return modifiers

    def update(self):
        if self._holding_now == 0 and (not self._is_dirty or not self.config.hotkeys):
            return

        current_pressed = set()

        pressed_modifiers = self._get_pressed_modifiers()
        key_getter = self.data.get

        for (key, modifiers), names in self.config.hotkeys.items():
            dict_key = (key, modifiers)
            if key_getter(key, False) and pressed_modifiers & modifiers == modifiers:
                current_pressed.add(dict_key)
                if dict_key not in self._last_frame_pressed:
                    self._notify_listeners(names, self.on_pressed_listeners)
                self._notify_listeners(names, self.on_holding_listeners)
            else:
                if dict_key in self._last_frame_pressed:
                    self._notify_listeners(names, self.on_released_listeners)

        self._last_frame_pressed = current_pressed
        self._is_dirty = False
