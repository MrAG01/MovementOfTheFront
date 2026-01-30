from enum import Enum


class ClientRequestType(Enum):
    PING = "ping"
    CONNECT = "connect"
    BUILD = "build"
    ADD_UNIT_IN_QUEUE = "add_unit_in_queue"
    BUILDING_SET_ENABLED = "building_set_enabled"
    BUILDING_SET_PRODUCTION = "building_set_production"
    DESTROY = "destroy"
    MAKE_NEW_UNIT_PATH = "make_new_unit_path"
    SET_SELF_MODE = "set_self_mode"
