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
