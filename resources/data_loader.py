import json
from components.building.building_config import BuildingConfig
from core.callback import Callback
from utils.os_utils import scan_folder_for_folders


class ModMetaData:
    def __init__(self, path):
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        self.name = data.get("name", "Unnamed Mod")
        self.priority = data.get("priority", 0)
        self.author = data.get("author", "Unknown")
        self.version = data.get("version", "1.0.0")
        self.game_version = data.get("game_version")
        self.description = data.get("description", "")
        self.dependencies = data.get("dependencies", [])


class ModData:
    def __init__(self, path):
        self._loaded = False
        self.buildings: dict[str, BuildingConfig] = {}
        self.units = {}

    def load(self):
        pass


class Mod:
    def __init__(self, path):
        self.base_path = path
        self.meta_data = ModMetaData(f"{path}/mod.json")
        self.mod_data = ModData(path)

    def load(self):
        self.mod_data.load()

    def get_metadata(self):
        return self.meta_data


class ModLoadError(Exception):
    ...


class DataLoader:
    def __init__(self, config_manager, default_data_path, mod_data_path):
        self.config_manager = config_manager
        self.default_data_path = default_data_path
        self.mod_data_path = mod_data_path
        self.true_data = Mod(self.default_data_path)

        self.listeners = []

        # name, Mod
        self.available_mods: dict[str, Mod] = {}
        self._scan_mods_folder()

    def add_listener(self, listener_callback):
        self.listeners.append(listener_callback)

    def remove_listener(self, listener_callback):
        if listener_callback in self.listeners:
            self.listeners.remove(listener_callback)

    def _send_message_to_listeners(self, message: Callback):
        for listener_callback in self.listeners:
            listener_callback(message)

    def _scan_mod(self, path):
        try:
            mod = Mod(path)
            metadata = mod.get_metadata()
            self.available_mods[metadata.name] = mod
        except (ModLoadError, FileNotFoundError) as error:
            self._send_message_to_listeners(Callback.error(f"Mod load error: {error}"))

    def _scan_mods_folder(self):
        mods = scan_folder_for_folders(self.mod_data_path)
        for mod in mods:
            self._scan_mod(mod)
