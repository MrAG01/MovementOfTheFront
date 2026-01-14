from enum import Enum


class ClientRequestType(Enum):
    PING = "ping"
    CONNECT = "connect"
    BUILD = "build"
    DESTROY = "destroy"
    SET_SELF_MODE = "set_self_mode"
