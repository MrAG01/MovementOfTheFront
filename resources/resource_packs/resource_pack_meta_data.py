import json
import os

from core.game_version import GameVersion
from resources.resource_packs.resource_packs_error_codes import ResourcePackLoadError
from resources.handlers.texture_handle import TextureHandle
from utils.os_utils import is_valid_path


class ResourcePackMetaData:
    def __init__(self, path):
        self.name: str = ""
        self.description: str = ""
        self.min_game_version: GameVersion = None

        self.preview_image: TextureHandle = None
        self.dependencies: list[str] = []
        self._load(path)

    def _load(self, path):
        metadata_path = os.path.join(path, "metadata.json")
        if not is_valid_path(metadata_path):
            raise ResourcePackLoadError("Cannot find metadata.json file")
        try:
            with open(metadata_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.name = data["name"]
                self.description = data.get("description", "")
                self.preview_image = TextureHandle(os.path.join(path, data["preview_image"])) if "preview_image" in data else None
                self.min_game_version = GameVersion.from_str(data["min_game_version"])
                self.dependencies = data.get("dependencies", [])
        except (FileNotFoundError, PermissionError) as error:
            raise ResourcePackLoadError(f"Metadata file load error: {error}.")
        except (json.JSONDecodeError, KeyError):
            raise ResourcePackLoadError(f"Cannot read {metadata_path}. It may be damaged.")
        except Exception as error:
            raise ResourcePackLoadError(f"Unexpected error while loading {metadata_path}: {error}.")

    def is_compatible_with(self, game_version: GameVersion) -> bool:
        if self.min_game_version is None:
            return True
        return game_version > self.min_game_version or game_version == self.min_game_version
