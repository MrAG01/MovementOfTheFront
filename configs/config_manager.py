from window_config import WindowConfig
import json


class ConfigManager:
    def __init__(self, path):
        self.window_config: WindowConfig = None
        self.window_config_subscribers = []

        self._load(path)

    def _apply_changes(self):
        pass

    def _load_window_config(self, path):
        try:
            with open(path, mode='r', encoding='utf-8') as file:
                data = json.load(file)
                self.window_config = WindowConfig(**data)
        except (FileNotFoundError, PermissionError, json.JSONDecodeError):
            self.window_config = WindowConfig.get_default()
        except Exception as error:
            print(f"Unexpected error: {error}")
            self.window_config = WindowConfig.get_default()

    def _load(self, path):
        self._load_window_config(path)

    def get_window_config(self):
        return self.window_config
