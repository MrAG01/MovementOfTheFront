import json
import os.path
from typing import Type, Any

import arcade
from arcade.gui import UIStyleBase, UISlider, UIInputText, UIWidget, UILabel
from arcade.gui.widgets.buttons import (UIFlatButton, UITextureButton)

from GUI.ui_color_rect import UIColorRect
from GUI.ui_texture import UITexture
from utils.os_utils import scan_folder_for_files_names, is_valid_path
from arcade.gui import UISpriteWidget


class Theme:
    def __init__(self, theme_filename, pack):
        self.pack = pack
        self.theme_filename = theme_filename
        self.widgets_data: dict[str, tuple[Type[UIWidget], dict[str, Any], dict[str, UIStyleBase]]] = {}
        self.available_widgets = set(scan_folder_for_files_names(self.theme_filename))
        self.styles_cache: dict[str, dict[str, UIStyleBase]] = {}

    @staticmethod
    def parse_type_str(type_str: str) -> Type[UIWidget]:
        widget_classes = {
            "UIFlatButton": UIFlatButton,
            "UITextureButton": UITextureButton,
            "UISlider": UISlider,
            "UIInputText": UIInputText,
            "UIColorRect": UIColorRect,
            "UILabel": UILabel,
            "UISpriteWidget": UISpriteWidget,
            "UITexture": UITexture
        }
        return widget_classes.get(type_str)

    def _load_style(self, widget_class, name):
        if name in self.styles_cache:
            return self.styles_cache[name]
        path = os.path.join(self.theme_filename, "styles", f"{name}.json")
        if is_valid_path(path):
            with open(path, "r", encoding="utf-8") as file:
                style = json.load(file)
                for style_key, style_data in style.items():
                    style[style_key] = widget_class.UIStyle(**style_data)
            self.styles_cache[name] = style
            return style

    def _load_widget(self, name):
        full_path = os.path.join(self.theme_filename, f"{name}.json")
        with open(full_path, 'r') as file:
            data = json.load(file)
        widget_class = Theme.parse_type_str(data["type"])
        if widget_class is None:
            return False
        if "style" in data:
            style = self._load_style(widget_class, data["style"])
        else:
            style = None

        _data = data.get("data", {})

        if "texture" in _data:
            _data["texture"] = self.pack.get_texture(_data["texture"]).get()
        if "sprite" in _data:
            texture = self.pack.get_texture(_data["sprite"]).get()
            _data["sprite"] = arcade.Sprite(texture)
        self.widgets_data[name] = (widget_class, _data, style)

    def get_widget_data(self, name: str) -> tuple[Type[UIWidget], dict[str, Any], dict[str, UIStyleBase]]:
        if name in self.widgets_data:
            return self.widgets_data.get(name)
        elif name in self.available_widgets:
            self._load_widget(name)
            if name in self.widgets_data:
                return self.widgets_data.get(name)
