import utils.os_utils as osu

class ResourcePack:
    def __init__(self, path):
        self.textures_handlers = {}


class ResourceManager:
    def __init__(self, resource_packs_path):
        self.resource_packs_path = resource_packs_path
        self.available_resource_packs = set()
        self._scan_resource_packs_folder()

        self.texture_handlers = {}
        self.

    def _scan_resource_packs_folder(self):
        self.available_resource_packs = set(osu.scan_folder_for_folders(self.resource_packs_path))

    def get_available_resource_packs(self):
        return self.available_resource_packs

