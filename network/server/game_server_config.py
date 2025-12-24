import hashlib


class GameServerConfig:
    def __init__(self, ip_address, max_players, password=None):
        self._ip_address = ip_address
        self._max_players = max_players
        self._has_password = password is not None
        self._password_hash = hashlib.sha256(password) if password is not None else None

    def get_ip(self):
        return self._ip_address

    def get_max_players(self):
        return self._max_players

    def has_password(self):
        return self._has_password

    def get_password_hash(self):
        return self._password_hash
