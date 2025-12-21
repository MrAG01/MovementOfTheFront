import json
import os.path
from typing import Type, Any
from arcade.gui import UIStyleBase, UISlider, UIInputText, UIWidget
from arcade.gui.widgets.buttons import (UIFlatButton, UITextureButton)
from utils.os_utils import scan_folder_for_files_names


class Theme:
    def __init__(self, theme_filename):
        self.theme_filename = theme_filename
        self.widgets_data: dict[str, tuple[Type[UIWidget], dict[str, Any], dict[str, UIStyleBase]]] = {}
        self.available_widgets = set(scan_folder_for_files_names(self.theme_filename))

    @staticmethod
    def parse_type_str(type_str: str) -> Type[UIWidget]:
        widget_classes = {
            "UIFlatButton": UIFlatButton,
            "UITextureButton": UITextureButton,
            "UISlider": UISlider,
            "UIInputText": UIInputText
        }
        return widget_classes.get(type_str)

    def _load_widget(self, name):
        full_path = os.path.join(self.theme_filename, f"{name}.json")
        with open(full_path, 'r') as file:
            data = json.load(file)
        widget_class = Theme.parse_type_str(data["type"])
        if widget_class is None:
            return False
        style = {}
        for style_key, style_data in data["style"].items():
            style[style_key] = widget_class.UIStyle(**style_data)

        self.widgets_data[name] = (widget_class, data.get("data", {}), style)

    def get_widget_data(self, name: str) -> tuple[Type[UIWidget], dict[str, Any], dict[str, UIStyleBase]]:
        if name in self.widgets_data:
            return self.widgets_data.get(name)
        elif name in self.available_widgets:
            self._load_widget(name)
            if name in self.widgets_data:
                return self.widgets_data.get(name)
