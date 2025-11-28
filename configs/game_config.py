from core.game_version import GameVersion


class GameConfig:
    def __init__(self):
        self._game_version = GameVersion.get_current()

    def get_game_version(self):
        return self._game_version