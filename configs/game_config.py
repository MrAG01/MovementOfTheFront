import os
from configs.base_config import BaseConfig
from core.game_version import GameVersion
from utils.constants import USER_DATA_PATH, SAVES_PATH


class GameConfig(BaseConfig):
    def __init__(self):
        self.saves_path = os.path.join(USER_DATA_PATH, SAVES_PATH)
        self._game_version = GameVersion.get_current()

    @classmethod
    def from_dict(cls, data):
        config = cls()
        config.saves_path = data["saves_path"]
        return config

    def serialize(self):
        return {}

    def get_game_version(self):
        return self._game_version
