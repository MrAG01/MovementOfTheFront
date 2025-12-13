from dataclasses import dataclass
from typing import Callable
import arcade.key

from configs.base_config import BaseConfig


@dataclass
class Hotkey(BaseConfig):
    key: int
    modifiers: int = 0
    pressed_callback: Callable = None
    holding_callback: Callable = None
    released_callback: Callable = None

    def _modifiers_to_str(self):
        modifiers_str_parts = []
        if self.modifiers & arcade.key.MOD_CTRL:
            modifiers_str_parts.append("Ctrl+")
        if self.modifiers & arcade.key.MOD_SHIFT:
            modifiers_str_parts.append("Shift+")
        if self.modifiers & arcade.key.MOD_ALT:
            modifiers_str_parts.append("Alt+")
        return "".join(modifiers_str_parts)

    @staticmethod
    def str_to_modifier(str_modifier):
        links = {
            "Ctrl": arcade.key.MOD_CTRL,
            "Shift": arcade.key.MOD_SHIFT,
            "Alt": arcade.key.MOD_ALT
        }
        return links[str_modifier]

    @staticmethod
    def convert_string_to_keys(bind):
        data = bind.split("+")
        if len(data) > 1:
            modifiers = 0
            for modifier_str in data[:-1]:
                modifiers |= Hotkey.str_to_modifier(modifier_str)
        else:
            modifiers = 0
        key = ord(data[-1].lower())
        return key, modifiers

    @classmethod
    def create(cls, bind, pressed_callback, holding_callback=None, released_callback=None):
        key, modifiers = Hotkey.convert_string_to_keys(bind)
        return cls(key=key,
                   modifiers=modifiers,
                   pressed_callback=pressed_callback,
                   holding_callback=holding_callback,
                   released_callback=released_callback)

    def make_pressed_callback(self):
        if self.pressed_callback is not None:
            self.pressed_callback()

    def make_holding_callback(self):
        if self.holding_callback is not None:
            self.holding_callback()

    def make_released_callback(self):
        if self.released_callback is not None:
            self.released_callback()

    def __str__(self):
        return self._modifiers_to_str() + chr(self.key).upper()

    def __hash__(self):
        return hash((self.key, self.modifiers))


class KeyboardManager:
    def __init__(self):
        self.hotkeys: dict[tuple[int, int], list[Hotkey]] = {}
        self.hotkeys_names: dict[str, Hotkey] = {}

        self.keys_holding: set[tuple[int, int]] = set()

    def unbind_key(self, name):
        if name not in self.hotkeys_names:
            return
        hotkey = self.hotkeys_names[name]
        dict_key = hotkey.key, hotkey.modifiers
        self.hotkeys[dict_key].remove(hotkey)
        del self.hotkeys_names[name]

    def bind_key(self, name, bind, pressed_callback, holding_callback=None, released_callback=None):
        key, modifiers = Hotkey.convert_string_to_keys(bind)
        hotkey = Hotkey(key, modifiers, pressed_callback, holding_callback, released_callback)
        dict_key = (key, modifiers)
        if dict_key in self.hotkeys:
            self.hotkeys[dict_key].append(hotkey)
        else:
            self.hotkeys[dict_key] = [hotkey]
        self.hotkeys_names[name] = hotkey

    def update(self):
        for dict_key in self.keys_holding:
            for hotkey in self.hotkeys[dict_key]:
                hotkey.make_holding_callback()

    def on_key_press(self, key: int, modifiers: int):
        dict_key = (key, modifiers)
        if dict_key in self.hotkeys:
            for hotkey in self.hotkeys[dict_key]:
                hotkey.make_pressed_callback()
            self.keys_holding.add(dict_key)

    def on_key_release(self, key: int, modifiers: int):
        dict_keys = (key, modifiers)
        if dict_keys in self.keys_holding:
            self.keys_holding.remove(dict_keys)
        if dict_keys in self.hotkeys:
            for hotkey in self.hotkeys[dict_keys]:
                hotkey.make_released_callback()

    def clear(self):
        self.hotkeys.clear()
        self.hotkeys_names.clear()

    def __contains__(self, name):
        return name in self.hotkeys_names
