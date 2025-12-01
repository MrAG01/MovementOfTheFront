from functools import lru_cache
import utils.os_utils as osu
from core.callback import Callback
from resources.resource_packs.resource_pack import ResourcePack
from resources.resource_packs.resource_pack_meta_data import ResourcePackMetaData
from resources.resource_packs.resource_packs_error_codes import ResourcePackLoadError


class ResourceManager:
    def __init__(self, config_manager, resource_packs_path):
        self.config_manager = config_manager
        self.resource_packs_path = resource_packs_path
        self.available_resource_packs = {}
        self.active_resource_packs = []
        self.listeners = []

    def reload(self):
        self._scan_resource_packs_folder()

    def get_texture(self, texture):
        for pack in self.active_resource_packs:
            if pack.has_texture(texture):
                return pack.get_texture(texture)

    def get_sound(self, texture):
        for pack in self.active_resource_packs:
            if pack.has_sound(texture):
                return pack.get_sound(texture)

    def get_music(self, texture):
        for pack in self.active_resource_packs:
            if pack.has_music(texture):
                return pack.get_music(texture)

    def get_font(self, texture):
        for pack in self.active_resource_packs:
            if pack.has_font(texture):
                return pack.get_font(texture)

    def add_listener(self, listener_callback):
        self.listeners.append(listener_callback)

    def remove_listener(self, listener_callback):
        if listener_callback in self.listeners:
            self.listeners.remove(listener_callback)

    def get_pack(self, name):
        return self.available_resource_packs.get(name)

    def has_pack(self, name):
        return name in self.available_resource_packs

    def use_resource_pack(self, pack_name, priority=-1):
        if not self.has_pack(pack_name):
            return False
        resource_pack = self.get_pack(pack_name)
        if resource_pack in self.active_resource_packs:
            self.active_resource_packs.remove(resource_pack)
        self.active_resource_packs.insert(priority, resource_pack)
        return True

    def _send_message_to_listeners(self, message: Callback):
        for listener_callback in self.listeners:
            listener_callback(message)

    def _scan_resource_packs_folder(self):
        packs = set(osu.scan_folder_for_folders(self.resource_packs_path))
        current_game_version = self.config_manager.get_game_version()
        for pack_path in packs:
            try:
                resource_pack = ResourcePack(pack_path)
                warnings = resource_pack.get_warnings()
                for warning in warnings:
                    self._send_message_to_listeners(warning)

                metadata: ResourcePackMetaData = resource_pack.metadata
                name = metadata.name

                if not metadata.is_compatible_with(current_game_version):
                    min_ver = metadata.min_game_version
                    raise ResourcePackLoadError(f"Resource pack '{name}' requires version {min_ver}+")

                self.available_resource_packs[name] = resource_pack

            except ResourcePackLoadError as error:
                self._send_message_to_listeners(Callback.error(f"Resource pack load error: {error}"))
                continue
            self._send_message_to_listeners(Callback.ok(f"Resource pack '{name}' loaded successfully"))

    def get_available_resource_packs(self):
        return self.available_resource_packs

    def get_available_resource_packs_metadata(self):
        return [pack.get_metadata() for pack in self.available_resource_packs.values()]
