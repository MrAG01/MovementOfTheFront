from core.callback import Callback
from resources.handlers.font_handle import FontHandle
from resources.handlers.music_handle import MusicHandle
from resources.handlers.sound_handle import SoundHandle
from resources.handlers.texture_handle import TextureHandle
from resources.resource_packs.resource_pack_meta_data import ResourcePackMetaData
from utils.os_utils import scan_folder_for_all_files, get_file_info, get_extension_type


class ResourcePack:
    def __init__(self, path):
        self.path = path

        self.metadata = ResourcePackMetaData(f"{self.path}/metadata.json")

        self.textures_handlers = {}
        self.sound_handlers = {}
        self.music_handlers = {}
        self.font_handlers = {}
        self.warnings = self._load(path)

    def get_warnings(self):
        return self.warnings

    def _is_duplicate(self, name, file_type):
        match file_type:
            case 'texture':
                return self.has_texture(name)
            case 'sound':
                return self.has_sound(name)
            case 'music':
                return self.has_music(name)
            case 'font':
                return self.has_font(name)
            case _:
                return False

    def _load(self, path):
        files = scan_folder_for_all_files(path)

        warnings = []

        for file in files:
            name, ext, full_path = get_file_info(file)
            file_type = get_extension_type(ext)
            if self._is_duplicate(name, file_type):
                warnings.append(Callback.warn(f"Duplicate resource: {name}.{ext}"))
                continue

            match file_type:
                case 'texture':
                    self.textures_handlers[name] = TextureHandle(full_path)
                case 'sound':
                    self.sound_handlers[name] = SoundHandle(full_path)
                case 'music':
                    self.music_handlers[name] = MusicHandle(full_path)
                case 'font':
                    self.font_handlers[name] = FontHandle(full_path)
                case _:
                    warnings.append(Callback.warn(f"Unknown extension: {name}.{ext}"))

        return warnings

    def has_texture(self, name):
        return name in self.textures_handlers

    def get_texture(self, name):
        return self.textures_handlers.get(name)

    def has_sound(self, name):
        return name in self.sound_handlers

    def get_sound(self, name):
        return self.sound_handlers.get(name)

    def has_music(self, name):
        return name in self.music_handlers

    def get_music(self, name):
        return self.music_handlers.get(name)

    def has_font(self, name):
        return name in self.font_handlers

    def get_font(self, name):
        return self.font_handlers.get(name)
