from resources.resource_packs.resource_pack_meta_data import ResourcePackMetaData


class ResourcePack:
    def __init__(self, path):
        self.path = path

        self.metadata = ResourcePackMetaData(f"{self.path}/metadata.json")

        self.textures_handlers = {}
        self.audio_handlers = {}
        self.font_handlers = {}
