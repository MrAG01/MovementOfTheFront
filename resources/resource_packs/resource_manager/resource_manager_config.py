from configs.base_config import BaseConfig
from configs.notification_mixin import NotificationMixin
from utils.constants import RESOURCE_PACKS_PATH


class ResourceManagerConfig(BaseConfig, NotificationMixin):
    def __init__(self):
        super().__init__()
        self.resource_packs_path = RESOURCE_PACKS_PATH
        self.language = "en"
        self.active_resource_packs = []

    def serialize(self):
        return {
            "resource_packs_path": self.resource_packs_path,
            "language": self.language,
            "active_resource_packs": self.active_resource_packs
        }

    @classmethod
    def from_dict(cls, data):
        config = cls()
        config.resource_packs_path = data["resource_packs_path"]
        config.language = data["language"]
        config.active_resource_packs = data["active_resource_packs"]
        return config

    def set_resource_pack_path(self, resource_packs_path):
        self.resource_packs_path = resource_packs_path

    def remove_pack(self, pack):
        if pack in self.active_resource_packs:
            self.active_resource_packs.remove(pack)
        self.notify_listeners()

    def insert_resource_pack(self, pack, priority=-1):
        if pack in self.active_resource_packs:
            self.active_resource_packs.remove(pack)
        if priority == -1:
            self.active_resource_packs.append(pack)
        else:
            priority = max(0, min(priority, len(self.active_resource_packs)))
            self.active_resource_packs.insert(priority, pack)
        self.notify_listeners()