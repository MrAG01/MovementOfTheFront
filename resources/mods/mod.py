from resources.mods.mod_data import ModData
from resources.mods.mod_meta_data import ModMetaData
from utils.constants import MOD_METADATA_PATH


class Mod:
    def __init__(self, path):
        self.base_path = path
        self.meta_data = ModMetaData(f"{path}/{MOD_METADATA_PATH}")
        self.mod_data = ModData(path)

    def load(self):
        self.mod_data.load()

    def unload(self):
        self.mod_data.unload()

    def get_priority(self):
        return self.meta_data.priority

    def has_building(self, building_name):
        return self.mod_data.has_building(building_name)

    def get_building(self, building_name):
        return self.mod_data.get_building(building_name)

    def get_metadata(self):
        return self.meta_data

    def has_biome(self, biome_name):
        return self.mod_data.has_biome(biome_name)

    def get_biome(self, biome_name):
        return self.mod_data.get_biome(biome_name)

    def get_load_callback(self):
        callbacks = [self.meta_data.get_load_message()]
        callbacks.extend(self.mod_data.get_warnings())
        return callbacks

    def get_buildings(self):
        return self.mod_data.get_buildings()