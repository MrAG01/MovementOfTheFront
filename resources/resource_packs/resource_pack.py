import os
from resources.resource_packs.resource_pack_meta_data import ResourcePackMetaData
from utils.os_utils import scan_folder_for_all_files, get_file_info


class ResourcePack:
    def __init__(self, path):
        self.path = path

        self.metadata = ResourcePackMetaData(f"{self.path}/metadata.json")

        self.textures_handlers = {}
        self.audio_handlers = {}
        self.font_handlers = {}
        self._load(path)

    def _load(self, path):
        files = scan_folder_for_all_files(path)
        for file in files:
            name, ext, path = get_file_info(file)




    def has_texture(self, name):
        return name in self.textures_handlers
