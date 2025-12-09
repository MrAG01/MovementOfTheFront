import json
from core.callback import Callback
from utils.os_utils import is_valid_path


class Locale:
    def __init__(self, path):
        self.path = path
        self.loaded = False
        self.data = {}

    def is_loaded(self):
        return self.loaded

    def unload(self):
        self.data.clear()
        self.loaded = False

    def _load(self):
        warnings = []
        if self.is_loaded():
            warnings.append(Callback.warn(f"Locale {self.path} already loaded"))
            return warnings
        if not is_valid_path(self.path):
            warnings.append(Callback.error(f"Cannot find locale file at '{self.path}'"))
            return warnings

        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
        except (FileNotFoundError, PermissionError) as error:
            warnings.append(Callback.error(f"Error while reading locale at {self.path}: {error}"))
        except json.JSONDecodeError as error:
            warnings.append(Callback.error(f"Cannot read locale at {self.path}, file may be corrupted: {error}"))
        self.loaded = True

    def get_located_text(self, text, cast):
        if not self.is_loaded():
            self._load()
        if cast not in self.data:
            return None
        return self.data[cast].get(text)
