import json
from game.building.building_config import BuildingConfig
from core.callback import Callback
from game.deposits.deposit_config import DepositConfig
from game.map.biome.biome import Biome
from resources.mods.mod_errors import ModLoadError
from utils.constants import BUILDINGS_PATH, BIOMES_PATH, DEPOSITS_PATH
from utils.os_utils import is_valid_path, scan_folder_for_all_files, get_file_info


class ModData:
    def __init__(self, path):
        self._loaded = False
        self.path = path
        self.buildings: dict[str, BuildingConfig] = {}
        self.biomes: dict[str, Biome] = {}
        self.warnings = []
        self.deposits: dict[str, DepositConfig] = {}
        # self.units: dict[str, UnitConfig] = {}

    def unload(self):
        self.buildings.clear()
        self.warnings.clear()
        self._loaded = False

    def _load_from(self, path, container, config_class):
        if is_valid_path(path):
            paths = scan_folder_for_all_files(path)
            for item_path in paths:
                try:
                    if not is_valid_path(item_path):
                        continue
                    with open(item_path, 'r', encoding='utf-8') as file:
                        name, ext, _ = get_file_info(item_path)
                        data = json.load(file)
                        container[name] = config_class.from_dict(data)
                except (FileNotFoundError, json.JSONDecodeError) as error:
                    self.warnings.append(Callback.warn(f"{item_path}: {error}"))

    def load(self):
        if self._loaded:
            return

        self._load_from(f'{self.path}/{BUILDINGS_PATH}', self.buildings, BuildingConfig)
        self._load_from(f'{self.path}/{BIOMES_PATH}', self.biomes, Biome)
        self._load_from(f'{self.path}/{DEPOSITS_PATH}', self.deposits, DepositConfig)

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

    def has_deposit(self, deposit_name):
        return deposit_name in self.deposits

    def get_deposit(self, deposit_name):
        return self.deposits.get(deposit_name)

    def get_deposits(self):
        self._check()
        return self.deposits
