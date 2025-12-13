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
