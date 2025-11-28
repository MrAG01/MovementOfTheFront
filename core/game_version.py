class GameVersion:
    def __init__(self, major: int, minor: int, patch: int):
        self.major: int = major
        self.minor: int = minor
        self.patch: int = patch

    def serialize(self):
        return {"version": str(self)}

    @classmethod
    def get_current(cls):
        # Писать сюда при каждом значимом изменении
        return cls(0, 1, 0)

    @classmethod
    def from_str(cls, version: str):
        return cls(*map(int, version.split(".")))

    @classmethod
    def from_dict(cls, data):
        return cls.from_str(data["version"])

    def is_compatible_with(self, other) -> bool:
        return self.major == other.major

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def __eq__(self, other):
        if not isinstance(other, GameVersion):
            return False
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __lt__(self, other):
        if not isinstance(other, GameVersion):
            raise TypeError(f"Expected {type(self).__name__} met {type(other).__name__}.")
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __gt__(self, other):
        return not self < other and not self == other
