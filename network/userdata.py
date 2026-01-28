from dataclasses import dataclass

from configs.base_config import BaseConfig


@dataclass
class UserData(BaseConfig):
    _username: str
    static_port: int

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, arg):
        self._username = arg

    @classmethod
    def from_dict(cls, data):
        return cls(_username=data["username"],
                   static_port=data["static_port"])

    def serialize(self):
        return {
            "username": self._username,
            "static_port": self.static_port
        }
