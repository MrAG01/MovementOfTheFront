from enum import Enum


class ClientRequestType(Enum):
    AUTH = "auth"
    MOUSE_CLICKED = "mouse_clicked"
