import json


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
        self.buildings = {}
        self.units = {}

    def load(self):
        pass


class Mod:
    def __init__(self, path):
        self.base_path = path
        self.meta_data = ModMetaData(f"{path}/mod.json")
        self.mod_data = ModData(path)


class DataLoader:
    def __init__(self, config_manager, default_data_path, mod_data_path):
        self.config_manager = config_manager
        self.default_data_path = default_data_path
        self.mod_data_path = mod_data_path
        self.true_data = Mod(self.default_data_path)

        # name, path
        self.available_mods: dict[str, str] = {}

    def _scan_mod_folder(self):
        pass
