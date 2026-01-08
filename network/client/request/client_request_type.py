from enum import Enum


class ClientRequestType(Enum):
    CONNECT = "connect"
    MOUSE_CLICKED = "mouse_clicked"
