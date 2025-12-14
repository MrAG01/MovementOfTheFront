from dataclasses import dataclass
from typing import Callable
import arcade.key
from configs.base_config import BaseConfig


class Hotkey:
    @staticmethod
    def modifiers_to_str(modifiers):
        modifiers_str_parts = []
        if modifiers & arcade.key.MOD_CTRL:
            modifiers_str_parts.append("Ctrl+")
        if modifiers & arcade.key.MOD_SHIFT:
            modifiers_str_parts.append("Shift+")
        if modifiers & arcade.key.MOD_ALT:
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