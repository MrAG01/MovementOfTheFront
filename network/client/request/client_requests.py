from dataclasses import dataclass
from network.client.request.client_request_type import ClientRequestType


@dataclass
class ClientRequest:
    type: ClientRequestType
    data: dict

    @classmethod
    def create_auth_request(cls, username, password, version):
        return cls(type=ClientRequestType.AUTH,
                   data={"username": username,
                         "password": password,
                         "version": version})

    @classmethod
    def create_mouse_pressed_request(cls, x, y):
        return cls(type=ClientRequestType.MOUSE_CLICKED,
                   data={"x": x,
                         "y": y})

    def serialize(self):
        return {"type": self.type,
                "data": self.data}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def __repr__(self):
        return f"ClientRequest(type={self.type}, data={self.data})"
