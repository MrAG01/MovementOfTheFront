class Item:
    def __init__(self, type, amount):
        self.item_type = type
        self.amount = amount

    def move(self, other, amount):
        if other.item_type != self.item_type:
            raise TypeError

        move_amount = min(amount, self.amount)
        self.amount -= move_amount
        other.amount += move_amount

    def add(self, amount):
        self.amount += amount

    def remove(self, amount):
        if self.amount >= amount:
            self.amount -= amount
            return True
        else:
            return False

    def has_amount(self, amount):
        return self.amount >= amount

    def set_amount(self, amount):
        self.amount = amount

    def copy(self):
        return Item(self.item_type, self.amount)

    def clear(self):
        self.amount = 0

    def __lt__(self, other):
        if isinstance(other, Item):
            return self.amount < other.amount
        elif isinstance(other, int) or isinstance(other, float):
            return self.amount < other
        else:
            return False

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.amount == other.amount and self.item_type == other.item_type
        elif isinstance(other, int) or isinstance(other, float):
            return self.amount == other
        else:
            return False

    def __add__(self, other):
        if isinstance(other, Item):
            if self.item_type != other.item_type:
                raise TypeError
            return Item(self.item_type, self.amount + other.amount)
        elif isinstance(other, int):
            return Item(self.item_type, self.amount + other)
        else:
            raise TypeError

    def __sub__(self, other):
        if isinstance(other, Item):
            if self.item_type != other.item_type:
                raise TypeError
            return Item(self.item_type, max(self.amount - other.amount, 0))
        elif isinstance(other, int):
            return Item(self.item_type, max(self.amount - other, 0))
        else:
            raise TypeError

    def __iadd__(self, other):
        if isinstance(other, Item):
            if self.item_type != other.item_type:
                raise TypeError
            self.amount += other.amount
        elif isinstance(other, int):
            self.amount += other
        else:
            raise TypeError
        return self

    def __int__(self):
        return int(self.amount)

    def __mul__(self, other):
        return Item(self.item_type, round(self.amount * other))

    def serialize(self):
        return {
            "type": self.item_type,
            "amount": self.amount
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
