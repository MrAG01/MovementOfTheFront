import hashlib
from dataclasses import dataclass
from network.client.request.client_request_type import ClientRequestType
from network.userdata import UserData


@dataclass
class ClientRequest:
    type: ClientRequestType
    data: dict

    @classmethod
    def create_connect_request(cls, user_data: UserData, password):
        data = {"user_data": user_data.serialize()}
        if password is not None:
            data["password"] = password
        return cls(type=ClientRequestType.CONNECT,
                   data=data)

    @classmethod
    def create_mouse_pressed_request(cls, x, y):
        return cls(type=ClientRequestType.MOUSE_CLICKED,
                   data={"x": x,
                         "y": y})

    def serialize(self):
        return {"type": self.type.value,
                "data": self.data}

    @classmethod
    def from_dict(cls, data):
        if "type" in data:
            data["type"] = ClientRequestType(data["type"])
        return cls(**data)

    def __repr__(self):
        return f"ClientRequest(type={self.type}, data={self.data})"
