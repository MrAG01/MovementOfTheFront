from enum import Enum


class ClientRequestType(Enum):
    CONNECT = "connect"
    BUILD = "build"
    SET_SELF_MODE = "set_self_mode"
