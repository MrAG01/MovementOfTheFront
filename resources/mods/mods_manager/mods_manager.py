from core.callback import Callback
from resources.mods.mod import Mod
from resources.mods.mod_errors import ModLoadError
from resources.mods.mods_manager.mods_manager_config import ModsManagerConfig
from utils.os_utils import scan_folder_for_folders


class ModsManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.mods_manager_config = self.config_manager.register_config("mods_manager_config", ModsManagerConfig)

        self.default_mod = Mod(self.mods_manager_config.default_data_path)
        self.listeners = []

        self.available_mods: dict[str, Mod] = {}
        self._scan_mods_folder()

        self._active_mods_relevant = False
        self._active_mods_ordered = []
        self.apply_mods()

    def get_biome(self, biome_name):
        self._try_to_regenerate_mods_order_cache()
        for mod in self._active_mods_ordered:
            if mod.has_biome(biome_name):
                return mod.get_biome(biome_name)
        return None

    def apply_mods(self):
        self._active_mods_ordered.clear()
        self.default_mod.load()
        for mod_name in self.mods_manager_config.active_mods:
            mod = self.available_mods[mod_name]
            mod.load()
        self._regenerate_active_mods_order_cache()

    def _try_to_regenerate_mods_order_cache(self):
        if self._active_mods_relevant:
            return
        self._regenerate_active_mods_order_cache()

    def _regenerate_active_mods_order_cache(self):
        self._active_mods_ordered.clear()
        self._active_mods_ordered = [self.available_mods[name] for name in self.mods_manager_config.active_mods]
        self._active_mods_ordered.append(self.default_mod)
        self._active_mods_ordered.sort(key=lambda mod: mod.get_priority(), reverse=True)
        self._active_mods_relevant = True

    def has_building(self, building_name):
        self._try_to_regenerate_mods_order_cache()
        for mod in self._active_mods_ordered:
            if mod.has_building(building_name):
                return True
        return False

    def get_building(self, building_name):
        self._try_to_regenerate_mods_order_cache()
        for mod in self._active_mods_ordered:
            if mod.has_building(building_name):
                return mod.get_building(building_name)
        return None

    def enable_mod(self, mod_name):
        if mod_name in self.available_mods:
            self.mods_manager_config.enable_mod(mod_name)
            self._active_mods_relevant = False

    def disable_mod(self, mod_name):
        if self.mods_manager_config.disable_mod(mod_name):
            self.available_mods[mod_name].unload()
            self._active_mods_relevant = False

    def set_mod_state(self, mod_name, state):
        if state:
            self.enable_mod(mod_name)
        else:
            self.disable_mod(mod_name)

    def add_listener(self, listener_callback):
        self.listeners.append(listener_callback)

    def remove_listener(self, listener_callback):
        if listener_callback in self.listeners:
            self.listeners.remove(listener_callback)

    def _send_message_to_listeners(self, message: Callback):
        for listener_callback in self.listeners:
            listener_callback(message)

    def _scan_mod(self, path):
        try:
            mod = Mod(path)
            metadata = mod.get_metadata()
            self.available_mods[metadata.name] = mod
            warnings = mod.get_load_callback()
            for warning in warnings:
                self._send_message_to_listeners(warning)

        except (ModLoadError, FileNotFoundError) as error:
            self._send_message_to_listeners(Callback.error(f"Mod load error: {error}"))

    def _scan_mods_folder(self):
        mods = scan_folder_for_folders(self.mods_manager_config.mod_data_path)
        for mod in mods:
            self._scan_mod(mod)

    def get_buildings(self):
        self._try_to_regenerate_mods_order_cache()
        all_buildings = {}
        for mod in self._active_mods_ordered:
            all_buildings |= mod.get_buildings()
        return all_buildings

    def get_deposit(self, deposit_name):
        self._try_to_regenerate_mods_order_cache()
        for mod in self._active_mods_ordered:
            if mod.has_deposit(deposit_name):
                return mod.get_deposit(deposit_name)
        return None

    def get_deposits(self):
        self._try_to_regenerate_mods_order_cache()
        all_deposits = {}
        for mod in self._active_mods_ordered:
            all_deposits |= mod.get_deposits()
        return all_deposits

    def get_unit(self, unit_name):
        self._try_to_regenerate_mods_order_cache()
        for mod in self._active_mods_ordered:
            if mod.has_unit(unit_name):
                return mod.get_unit(unit_name)
        return None

    def get_units(self):
        self._try_to_regenerate_mods_order_cache()
        all_units = {}
        for mod in self._active_mods_ordered:
            all_units |= mod.get_units()
        return all_units
