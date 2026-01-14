import hashlib
import time
from dataclasses import dataclass

from game.deposits.client_deposit import ClientDeposit
from network.client.request.client_request_type import ClientRequestType
from network.userdata import UserData


@dataclass
class ClientRequest:
    type: ClientRequestType
    data: dict

    @classmethod
    def create_ping_request(cls):
        return cls(type=ClientRequestType.PING,
                   data={
                       "time": time.time()
                   })

    @classmethod
    def create_destroy_request(cls, building_id):
        return cls(type=ClientRequestType.DESTROY,
                   data={"building_id": building_id})

    @classmethod
    def create_connect_request(cls, user_data: UserData, password):
        data = {"user_data": user_data.serialize(),
                "time": time.time()}
        if password is not None:
            data["password"] = password
        return cls(type=ClientRequestType.CONNECT,
                   data=data)

    @classmethod
    def create_build_request(cls, x, y, building_type, linked_deposit: ClientDeposit = None):
        data = {
            "x": x,
            "y": y,
            "building_type": building_type
        }
        if linked_deposit is not None:
            data["linked_deposit"] = linked_deposit.deposit_id
        return cls(type=ClientRequestType.BUILD,
                   data=data)

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
