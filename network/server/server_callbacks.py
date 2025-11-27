from dataclasses import dataclass


@dataclass
class ServerCallback:
    is_error: bool
    message: str

    @classmethod
    def ok(cls, message, **kwargs):
        return cls(is_error=False, message=message, **kwargs)

    @classmethod
    def error(cls, message, **kwargs):
        return cls(is_error=True, message=message, **kwargs)