from core.callback import Callback
from resources.mods.mod import Mod
from resources.mods.mod_errors import ModLoadError
from utils.os_utils import scan_folder_for_folders


class ModsManager:
    def __init__(self, config_manager, default_data_path, mod_data_path):
        self.config_manager = config_manager
        self.default_data_path = default_data_path
        self.mod_data_path = mod_data_path
        self.default_mod = Mod(self.default_data_path)

        self.listeners = []

        self.available_mods: dict[str, Mod] = {}
        self.active_mods: set[str] = set()
        self._scan_mods_folder()

        self._active_mods_relevant = False
        self._active_mods_ordered = []

    def apply_mods(self):
        self._active_mods_ordered.clear()
        self.default_mod.load()
        for mod_name in self.active_mods:
            mod = self.available_mods[mod_name]
            mod.load()
        self._regenerate_active_mods_order_cache()

    def _try_to_regenerate_mods_order_cache(self):
        if self._active_mods_relevant:
            return
        self._regenerate_active_mods_order_cache()

    def _regenerate_active_mods_order_cache(self):
        self._active_mods_ordered.clear()
        self._active_mods_ordered = [self.available_mods[name] for name in self.active_mods]
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
            self.active_mods.add(mod_name)
            self._active_mods_relevant = False

    def disable_mod(self, mod_name):
        if mod_name in self.active_mods:
            self.active_mods.remove(mod_name)
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
        mods = scan_folder_for_folders(self.mod_data_path)
        for mod in mods:
            self._scan_mod(mod)
