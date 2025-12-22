import utils.os_utils as osu
from components.animation import Animation
from configs.config_manager import ConfigManager
from core.callback import Callback
from resources.resource_packs.resource_manager.resource_manager_config import ResourceManagerConfig
from resources.resource_packs.resource_pack import ResourcePack
from resources.resource_packs.resource_pack_meta_data import ResourcePackMetaData
from resources.resource_packs.resource_packs_error_codes import ResourcePackLoadError


class ResourceManager:
    def __init__(self, config_manager):
        self.config_manager: ConfigManager = config_manager
        self.resource_manager_config = self.config_manager.register_config("resource_manager_config",
                                                                           ResourceManagerConfig)

        self.available_resource_packs = {}
        self.listeners = []

        self._resources_cache = {}
        self.reload()

    def reload(self):
        self._resources_cache.clear()
        self._scan_resource_packs_folder()

    def get_animation(self, name, animation_fps=24, repeat=True, reset_on_replay=True, _class=Animation):
        for pack_name in self.resource_manager_config.active_resource_packs:
            if pack_name not in self.available_resource_packs:
                continue
            pack = self.available_resource_packs[pack_name]

            if pack.has_animation(name):
                return pack.get_animation(name,
                                          animation_fps=animation_fps,
                                          repeat=repeat,
                                          reset_on_replay=reset_on_replay,
                                          _class=_class)

    def _get_resource(self, name, resource_name):
        cache_key = (resource_name, name)
        if cache_key in self._resources_cache:
            return self._resources_cache[cache_key]

        has_checker_name = f"has_{resource_name}"
        for pack_name in self.resource_manager_config.active_resource_packs:
            if pack_name not in self.available_resource_packs:
                continue
            pack = self.available_resource_packs[pack_name]
            has_checker = getattr(pack, has_checker_name, None)
            if has_checker and has_checker(name):
                resource = getattr(pack, f"get_{resource_name}")(name)
                self._resources_cache[cache_key] = resource
                return resource

    def get_texture(self, name):
        return self._get_resource(name, "texture")

    def get_sound(self, name):
        return self._get_resource(name, "sound")

    def get_music(self, name):
        return self._get_resource(name, "music")

    def get_font(self, name):
        return self._get_resource(name, "font")

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
        self.resource_manager_config.insert_resource_pack(pack_name, priority)
        return True

    def get_located_text(self, text, cast):
        for pack_name in self.resource_manager_config.active_resource_packs:
            if pack_name not in self.available_resource_packs:
                continue
            pack: ResourcePack = self.available_resource_packs[pack_name]
            located_text = pack.get_located_text(text, cast, self.resource_manager_config.language)
            if located_text is not None:
                return located_text
        return "Unnamed"

    def _send_message_to_listeners(self, message: Callback):
        for listener_callback in self.listeners:
            listener_callback(message)

    def _scan_resource_packs_folder(self):
        packs = set(osu.scan_folder_for_folders(self.resource_manager_config.resource_packs_path))
        current_game_version = self.config_manager.get_config("game_config").get_game_version()
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

    def create_widget(self, name, **kwargs):
        kwargs["text"] = self.get_located_text(name, "gui")
        for pack_name in self.resource_manager_config.active_resource_packs:
            if pack_name not in self.available_resource_packs:
                continue
            pack: ResourcePack = self.available_resource_packs[pack_name]
            widget = pack.create_widget(name, **kwargs)
            if widget is not None:
                return widget
        return None

    def get_available_resource_packs(self):
        return self.available_resource_packs

    def get_available_resource_packs_metadata(self):
        return [pack.get_metadata() for pack in self.available_resource_packs.values()]

    def get_biomes_colors(self):
        all_biomes_colors = {}
        for pack_name in self.resource_manager_config.active_resource_packs:
            if pack_name not in self.available_resource_packs:
                continue
            pack: ResourcePack = self.available_resource_packs[pack_name]
            all_biomes_colors |= pack.get_biomes_colors()
        return all_biomes_colors
