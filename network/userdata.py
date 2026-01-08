from dataclasses import dataclass

from configs.base_config import BaseConfig


@dataclass
class UserData(BaseConfig):
    username: str

    def serialize(self):
        return {
            "username": self.username
        }
