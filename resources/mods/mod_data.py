import json
from game.building.building_config import BuildingConfig
from core.callback import Callback
from game.map.biome.biome import Biome
from resources.mods.mod_errors import ModLoadError
from utils.constants import BUILDINGS_PATH, BIOMES_PATH
from utils.os_utils import is_valid_path, scan_folder_for_all_files, get_file_info


class ModData:
    def __init__(self, path):
        self._loaded = False
        self.path = path
        self.buildings: dict[str, BuildingConfig] = {}
        self.biomes: dict[str, Biome] = {}
        self.warnings = []
        # self.deposits: dict[str, DepositConfig] = {}
        # self.units: dict[str, UnitConfig] = {}

    def unload(self):
        self.buildings.clear()
        self.warnings.clear()
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        buildings_folder_path = f'{self.path}/{BUILDINGS_PATH}'
        if is_valid_path(buildings_folder_path):
            buildings_paths = scan_folder_for_all_files(buildings_folder_path)
            for building_path in buildings_paths:
                try:
                    if not is_valid_path(building_path):
                        continue
                    with open(building_path, 'r', encoding='utf-8') as file:
                        name, ext, _ = get_file_info(building_path)
                        data = json.load(file)
                        self.buildings[name] = BuildingConfig.from_dict(data)
                except (FileNotFoundError, json.JSONDecodeError) as error:
                    self.warnings.append(Callback.warn(f"{building_path}: {error}"))
        biomes_folder_path = f'{self.path}/{BIOMES_PATH}'
        if is_valid_path(biomes_folder_path):
            biomes_paths = scan_folder_for_all_files(biomes_folder_path)
            for biome_path in biomes_paths:
                try:
                    if not is_valid_path(biome_path):
                        continue
                    with open(biome_path, 'r', encoding='utf-8') as file:
                        name, ext, _ = get_file_info(biome_path)
                        data = json.load(file)
                        self.biomes[name] = Biome.from_dict(data)
                except (FileNotFoundError, json.JSONDecodeError) as error:
                    self.warnings.append(Callback.warn(f"{biome_path}: {error}"))
        self._loaded = True

    def get_warnings(self):
        return self.warnings

    def _check(self):
        if not self._loaded:
            raise ModLoadError("You cannot use an unloaded mod.")

    def has_building(self, building_name):
        return building_name in self.buildings

    def get_building(self, building_name):
        self._check()
        return self.buildings.get(building_name)

    def has_biome(self, biome_name):
        return biome_name in self.biomes

    def get_biome(self, biome_name):
        self._check()
        return self.biomes.get(biome_name)

    def get_buildings(self):
        self._check()
        return self.buildings
