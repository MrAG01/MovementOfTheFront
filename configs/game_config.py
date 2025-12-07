from configs.base_config import BaseConfig
from core.game_version import GameVersion


class GameConfig(BaseConfig):
    def __init__(self):
        self._game_version = GameVersion.get_current()

    @classmethod
    def from_dict(cls, data):
        config = cls()
        return config

    def serialize(self):
        return {}

    def get_game_version(self):
        return self._game_version
