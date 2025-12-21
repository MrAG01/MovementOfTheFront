import os.path

from components.animation import Animation
from core.callback import Callback
from resources.handlers.font_handle import FontHandle
from resources.handlers.music_handle import MusicHandle
from resources.handlers.sound_handle import SoundHandle
from resources.handlers.texture_handle import TextureHandle
from resources.resource_packs.locale import Locale
from resources.resource_packs.resource_pack_meta_data import ResourcePackMetaData
from resources.resource_packs.theme import Theme
from utils.os_utils import scan_folder_for_all_files, get_file_info, get_extension_type, scan_folder_for_files


class ResourcePack:
    def __init__(self, path):
        self.path = path

        self.metadata = ResourcePackMetaData(f"{self.path}/metadata.json")

        self.animations = {}
        self.textures_handlers = {}
        self.sound_handlers = {}
        self.music_handlers = {}
        self.font_handlers = {}

        self.locales = {}
        self.theme = Theme(os.path.join(self.path, "theme"))

        self.warnings = self._load(path)

    def create_widget(self, name, **kwargs):
        widget_data = self.theme.get_widget_data(name)
        if widget_data is None:
            self.warnings.append(Callback.error("Cannot create widget."))
            return None
        widget_class, data, widget_style = widget_data
        return widget_class(style=widget_style, **kwargs, **data)

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

    def _find_animations(self):
        animations = {}
        for name, handler in self.textures_handlers.items():
            data = name.split("_")
            if not data or not data[-1].isdigit():
                continue
            animation_name, frame_id = "_".join(data[:-1]), int(data[-1])

            if animation_name in animations:
                animations[animation_name].append((frame_id, handler))
            else:
                animations[animation_name] = [(frame_id, handler)]
        for name, animation_raw in animations.items():
            animation_raw.sort(key=lambda el: el[0])
            self.animations[name] = [handler for index, handler in animation_raw]

    def has_animation(self, name):
        return name in self.animations

    def get_animation(self, name, animation_fps=24, repeat=True, reset_on_replay=True, _class=Animation):
        if not self.has_animation(name):
            return None
        return _class(frames=self.animations[name],
                      animation_fps=animation_fps,
                      repeat=repeat,
                      reset_on_replay=reset_on_replay)

    def _load_locales(self, locales_path):
        available_locales_files = scan_folder_for_files(locales_path)
        for path in available_locales_files:
            name, ext, full_path = get_file_info(path)
            self.locales[name] = Locale(full_path)

    def _load(self, path):
        files = scan_folder_for_all_files(path, _except=["locales", "metadata.json"])

        warnings = []
        for file in files:
            name, ext, full_path = get_file_info(file)
            file_type = get_extension_type(ext[1::])
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
        self._find_animations()
        self._load_locales(str(os.path.join(self.path, "locales")))
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

    def get_located_text(self, text, cast, language="en"):
        if language not in self.locales:
            return None
        return self.locales[language].get_located_text(text, cast)
