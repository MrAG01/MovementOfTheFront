from enum import Enum


class ClientRequestType(Enum):
    PING = "ping"
    CONNECT = "connect"
    BUILD = "build"
    ADD_UNIT_IN_QUEUE = "add_unit_in_queue"
    DESTROY = "destroy"
    SET_SELF_MODE = "set_self_mode"
