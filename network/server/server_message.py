from enum import Enum


class ServerResponseType(Enum):
    SNAPSHOT = "snapshot"
    DISCONNECT = "disconnect"
    ERROR = "error"


class ServerResponse:
    def __init__(self, type, data):
        self.type: ServerResponseType = type
        self.data = data

    @classmethod
    def create_snapshot(cls, snapshot: dict):
        return cls(type=ServerResponseType.SNAPSHOT,
                   data=snapshot)

    @classmethod
    def create_disconnect_message(cls, message):
        return cls(type=ServerResponseType.DISCONNECT,
                   data=message)

    @classmethod
    def create_error_message(cls, message):
        return cls(type=ServerResponseType.ERROR,
                   data=message)

    def serialize(self):
        return {
            "type": self.type.value,
            "data": self.data
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
