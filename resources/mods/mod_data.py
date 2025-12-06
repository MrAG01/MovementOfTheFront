import json
from components.building.building_config import BuildingConfig
from core.callback import Callback
from resources.mods_manager import ModLoadError
from utils.constants import BUILDINGS_PATH
from utils.os_utils import is_valid_path, scan_folder_for_all_files, get_file_info


class ModData:
    def __init__(self, path):
        self._loaded = False
        self.path = path
        self.buildings: dict[str, BuildingConfig] = {}
        self.warnings = []
        # self.units: dict[str, UnitConfig] = {}
        # self.deposits: dict[str, DepositConfig] = {}

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