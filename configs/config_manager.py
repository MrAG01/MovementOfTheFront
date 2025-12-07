from configs.game_config import GameConfig
from configs.window_config import WindowConfig
import json
from utils.os_utils import generate_dirs


class ConfigManager:
    def __init__(self, path):
        self._window_config: WindowConfig = WindowConfig.get_default()
        self._game_config: GameConfig = GameConfig.get_default()
        self._window_config_listeners = []
        self._listeners = {}
        self._load(path)

    def get_game_version(self):
        return self._game_config.get_game_version()

    def add_listener(self, callback, config_type):
        if config_type in self._listeners:
            self._listeners[config_type].append(callback)
        else:
            self._listeners[config_type] = [callback]

    def remove_listener(self, callback, config_type):
        if config_type not in self._listeners:
            return
        if callback in self._listeners[config_type]:
            self._listeners[config_type].remove(callback)

    def _apply_changes(self, config_type):
        if config_type not in self._listeners:
            return
        for listener_callback in self._listeners[config_type]:
            listener_callback(self)

    def _load_window_config(self, path):
        try:
            with open(path, mode='r', encoding='utf-8') as file:
                data = json.load(file)
                self._window_config = WindowConfig.from_dict(data)
        except (FileNotFoundError, PermissionError, json.JSONDecodeError):
            self._window_config = WindowConfig.get_default()
        except Exception as error:
            print(f"Unexpected error: {error}")
            self._window_config = WindowConfig.get_default()

    def _save_window_config(self, path):
        try:
            generate_dirs(path)
            with open(path, mode='w', encoding='utf-8') as file:
                data = self._window_config.serialize()
                json.dump(data, file, indent=2)
        except Exception as error:
            print(f"Unexpected error while saving config: {error}")

    def _load(self, path):
        self._load_window_config(f"{path}/window_config.json")

    def save(self, path):
        self._save_window_config(f"{path}/window_config.json")

    def get_window_config(self):
        return self._window_config

    # region WINDOW CONFIG REGION
    def set_resolution(self, resolution):
        self._window_config.set_width(resolution[0])
        self._window_config.set_height(resolution[1])
        self._apply_changes(WindowConfig)

    def set_screen_width(self, width):
        self._window_config.set_width(width)
        self._apply_changes(WindowConfig)

    def set_screen_height(self, height):
        self._window_config.set_height(height)
        self._apply_changes(WindowConfig)

    def set_vsync(self, vsync):
        self._window_config.vsync = vsync
        self._apply_changes(WindowConfig)

    def set_fps(self, fps):
        self._window_config.set_fps(fps)
        self._apply_changes(WindowConfig)

    def set_fullscreen(self, fullscreen):
        self._window_config.fullscreen = fullscreen
        self._apply_changes(WindowConfig)

    def set_resizable(self, resizable):
        self._window_config.resizable = resizable
        self._apply_changes(WindowConfig)

    def set_auto_window_resize(self, arg):
        self._window_config.set_auto_window_resize(arg)
        self._apply_changes(WindowConfig)

    # endregion WINDOW CONFIG REGION
