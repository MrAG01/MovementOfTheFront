from resources.handlers.resource_handle import ResourceHandle
import arcade

from utils.os_utils import get_file_info


class FontHandle(ResourceHandle):
    def __init__(self, *args):
        super().__init__(*args)
        self._load()

    def _load(self):
        name, ext, full_path = get_file_info(self.path)
        self._font = arcade.load_font(full_path)
        self.resource = name
        self._loaded = True
