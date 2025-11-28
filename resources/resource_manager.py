import utils.os_utils as osu
from core.game_version import GameVersion
from resources.texture_handle import TextureHandle


class ResourcePackLoadError(Exception):
    ...


class ResourcePackMetaData:
    def __init__(self, path):
        self.name: str = ""
        self.description: str = ""
        self.preview_image = TextureHandle = None
        self.min_game_version = GameVersion = None
        self.dependencies: list[str] = []
        self._load(path)

    def _load(self, path):
        pass


class ResourcePack:
    def __init__(self, path):
        self.path = path

        self._load_metadata(f"{self.path}/metadata.json")

        self.textures_handlers = {}
        self.audio_handlers = {}
        self.font_handlers = {}
        self._loaded = False

    def _load_metadata(self, path):
        pass

    def _load(self):
        pass


class ResourceManager:
    def __init__(self, resource_packs_path):
        self.resource_packs_path = resource_packs_path
        self.available_resource_packs = {}
        self._scan_resource_packs_folder()

        self.active_resource_packs = []

    def get_resource_pack(self, name):
        return self.available_resource_packs.get(name)

    def use_resource_pack(self, pack_name, priority=-1):
        resource_pack = self.get_resource_pack(pack_name)
        if resource_pack in self.active_resource_packs:
            self.active_resource_packs.remove(resource_pack)
        self.active_resource_packs.insert(priority, resource_pack)

    def _scan_resource_packs_folder(self):
        packs = set(osu.scan_folder_for_folders(self.resource_packs_path))
        for pack_path in packs:
            resource_pack = ResourcePack(pack_path)

    def get_available_resource_packs(self):
        return self.available_resource_packs
