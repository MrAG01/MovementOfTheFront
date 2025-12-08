from configs.base_config import BaseConfig
from configs.notification_mixin import NotificationMixin
from utils.constants import DEFAULT_MODE_PATH, MODS_PATH


class ModsManagerConfig(BaseConfig, NotificationMixin):
    def __init__(self):
        super().__init__()
        self.default_data_path: str = DEFAULT_MODE_PATH
        self.mod_data_path: str = MODS_PATH
        self.active_mods: set[str] = set()

    def serialize(self):
        return {
            "default_data_path": self.default_data_path,
            "mod_data_path": self.mod_data_path,
            "active_mods": list(self.active_mods),
        }

    @classmethod
    def from_dict(cls, data):
        config = cls.get_default()
        config.default_data_path = data["default_data_path"]
        config.mod_data_path = data["mod_data_path"]
        config.active_mods = set(data["active_mods"])
        return config

    def set_default_data_path(self, path):
        self.default_data_path = path
        self.notify_listeners()

    def set_mod_data_path(self, path):
        self.mod_data_path = path
        self.notify_listeners()

    def enable_mod(self, mod_name):
        self.active_mods.add(mod_name)
        self.notify_listeners()

    def disable_mod(self, mod_name):
        if mod_name in self.active_mods:
            self.active_mods.remove(mod_name)
            self.notify_listeners()
            return True
        return False