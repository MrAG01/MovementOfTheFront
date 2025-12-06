import json
from core.callback import Callback


class ModMetaData:
    def __init__(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.name = data.get("name", "Unnamed Mod")
            self.priority = data.get("priority", 0)
            self.author = data.get("author", "Unknown")
            self.version = data.get("version", "1.0.0")
            self.game_version = data.get("game_version")
            self.description = data.get("description", "")
            self.dependencies = data.get("dependencies", [])
            self.valid = True
            self.message = Callback.ok(f"{path}: Loaded successfully")
        except (FileNotFoundError, json.JSONDecodeError) as error:
            self.valid = False
            self.message = Callback.error(f"{path}: {error}")

    def is_valid(self):
        return self.valid

    def get_load_message(self):
        return self.message
