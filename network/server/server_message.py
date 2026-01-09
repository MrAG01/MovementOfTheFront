from enum import Enum


class ServerResponseType(Enum):
    SNAPSHOT = "snapshot"
    PLAYER_LIST = "player_list"
    DISCONNECT = "disconnect"
    CONNECT_MESSAGE = "connect_message"
    ERROR = "error"


class ServerResponse:
    def __init__(self, type, data):
        self.type: ServerResponseType = type
        self.data = data

    @classmethod
    def create_connect_message(cls, player_id):
        return cls(type=ServerResponseType.CONNECT_MESSAGE,
                   data=player_id)

    @classmethod
    def create_snapshot(cls, snapshot: dict):
        return cls(type=ServerResponseType.SNAPSHOT,
                   data=snapshot)

    @classmethod
    def create_player_list(cls, client_names):
        return cls(type=ServerResponseType.PLAYER_LIST,
                   data=client_names)

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
        return cls(type=ServerResponseType(data["type"]), data=data["data"])

    def __repr__(self):
        return f"ServerResponse(type={self.type.value}, data={self.data})"
