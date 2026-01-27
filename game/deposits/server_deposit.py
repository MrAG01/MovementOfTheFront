import random
from typing import Optional
from components.items import Items
from game.actions.events import Event, BuildingEvents
from game.building.server_building import ServerBuilding
from game.deposits.deposit_config import DepositConfig


class ServerDeposit:
    def __init__(self, deposit_id, deposit_config: DepositConfig, position):
        self.deposit_id = deposit_id

        self.deposit_config = deposit_config
        self.position = position
        self.deposit_capacity = random.randint(deposit_config.min_capacity, deposit_config.max_capacity)
        self.max_deposit_capacity = self.deposit_capacity

        self.owned_mine: Optional[ServerBuilding] = None

        # example -> {"time": 5, "production": Items(...)}
        self._product_condition_cache = None
        self.production_timer = None

        self.dirty = False
        self.attached_server_map = None

    def attach_server_map(self, map):
        if self.attached_server_map is not None:
            self.attached_server_map.deposit_stopped(self)
        self.attached_server_map = map

    def make_dirty(self):
        self.dirty = True

    def is_dirty(self):
        return self.dirty

    def detach_mine(self):
        if self.owned_mine is not None:
            self.owned_mine = None
            self._product_condition_cache = None
            self.production_timer = None
            if self.attached_server_map:
                self.attached_server_map.deposit_stopped(self)
            self.make_dirty()

    def try_attach_owned_mine(self, owned_mine: ServerBuilding):
        if self.owned_mine is not None:
            return False

        if owned_mine.config.name not in self.deposit_config.product_buildings:
            return False

        self.owned_mine = owned_mine
        if self.attached_server_map:
            self.attached_server_map.deposit_working(self)

        self._product_condition_cache = self.deposit_config.product_buildings[owned_mine.config.name]
        self.production_timer = self._product_condition_cache["time"]
        self.owned_mine.add_event(Event(BuildingEvents.PRODUCTION_STARTED, {"time": self.production_timer}))
        owned_mine.set_linked_deposit(self)
        self.make_dirty()
        return True

    def update(self, delta_time):
        #print(self.production_timer)
        if self.owned_mine is None or not self.owned_mine.working():
            return

        self.production_timer -= delta_time
        if self.production_timer <= 0:
            inventory: Items = self.owned_mine.owner_player.inventory
            inventory.adds(self._product_condition_cache["production"])
            self.production_timer = self._product_condition_cache["time"]
            self.owned_mine.add_event(Event(BuildingEvents.PRODUCTION_STARTED, {"time": self.production_timer}))

    def serialize_static(self):
        return {
            "deposit_id": self.deposit_id,
            "deposit_config": self.deposit_config.name,
            "position": [self.position.x, self.position.y],
            "deposit_max_capacity": self.max_deposit_capacity
        } | self.serialize_dynamic()

    def serialize_dynamic(self):
        self.dirty = False
        return {
            "owned_mine_id": self.owned_mine.id if self.owned_mine is not None else None
        }
