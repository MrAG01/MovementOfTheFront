class BaseConfig:
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def serialize(self):
        return self.__dict__

    @classmethod
    def get_default(cls):
        return cls()
