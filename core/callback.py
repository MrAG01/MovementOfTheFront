from dataclasses import dataclass
from enum import Enum


class CallbackType(Enum):
    SUCCESS = 1
    WARNING = 2
    ERROR = 3


@dataclass
class Callback:
    callback_type: CallbackType
    message: str

    @classmethod
    def ok(cls, message, **kwargs):
        return cls(callback_type=CallbackType.SUCCESS, message=message, **kwargs)

    @classmethod
    def warn(cls, message, **kwargs):
        return cls(callback_type=CallbackType.WARNING, message=message, **kwargs)

    @classmethod
    def error(cls, message, **kwargs):
        return cls(callback_type=CallbackType.ERROR, message=message, **kwargs)

    def _get_callback_type_str(self):
        return self.callback_type.name

    def is_error(self):
        return self.callback_type == CallbackType.ERROR

    def is_warning(self):
        return self.callback_type == CallbackType.WARNING

    def is_success(self):
        return self.callback_type == CallbackType.SUCCESS

    def __str__(self):
        return f'{self._get_callback_type_str()}: {self.message}'
