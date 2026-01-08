import hashlib


class GameServerConfig:
    def __init__(self, name, max_players, password=None):
        self.server_name = name
        self._max_players = max_players
        self._has_password = password is not None
        self._password = password

    def get_max_players(self):
        return self._max_players

    def has_password(self):
        return self._has_password

    def get_password(self):
        return self._password

    def serialize_for_server_logger(self):
        return {
            "server_name": self.server_name,
            "max_players": self._max_players,
            "has_password": self._has_password
        }
