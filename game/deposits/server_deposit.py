import random
from typing import Optional
import arcade
from components.items import Items
from game.building.server_building import ServerBuilding
from game.deposits.deposit_config import DepositConfig
from network.network_object import NetworkObject
from resources.handlers.texture_handle import TextureHandle
from resources.mods.mods_manager.mods_manager import ModsManager
from resources.resource_packs.resource_manager.resource_manager import ResourceManager


class ClientDeposit:
    def __init__(self, resource_manager, mods_manager, snapshot):
        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager: ModsManager = mods_manager
        self.deposit_id = snapshot["deposit_id"]

        self.config: DepositConfig = self.mods_manager.get_deposit(snapshot["deposit_config"])
        self.texture: TextureHandle = self.resource_manager.get_texture(self.config.name)

        self.position = arcade.Vec2(*snapshot["position"])
        self.deposit_capacity = snapshot["deposit_capacity"]
        self.deposit_max_capacity = snapshot["deposit_max_capacity"]

    def update_from_snapshot(self, snapshot):
        self.deposit_capacity = snapshot["deposit_capacity"]

    def draw(self, camera):
        zoom_k = 1 / camera.zoom
        #print(self.position.x, self.position.y)
        self.texture.draw(self.position.x, self.position.y, zoom_k, zoom_k,
                          alpha=255 * (self.deposit_capacity / self.deposit_max_capacity))


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

    def make_dirty(self):
        self.dirty = True

    def is_dirty(self):
        return self.dirty

    def detach_mine(self):
        self.owned_mine = None
        self._product_condition_cache = None
        self.production_timer = None

    def try_attach_owned_mine(self, owned_mine: ServerBuilding):
        if self.owned_mine is not None:
            return False

        if owned_mine.config.name not in self.deposit_config.product_buildings:
            return False

        self.owned_mine = owned_mine
        self._product_condition_cache = self.deposit_config.product_buildings[owned_mine.config.name]
        self.production_timer = self._product_condition_cache["time"]

        return True

    def update(self, delta_time):
        if self.owned_mine is None or not self.owned_mine.working():
            return
        if self.deposit_capacity <= 0:
            return
        self.production_timer -= delta_time
        if self.production_timer <= 0:
            inventory: Items = self.owned_mine.owner_player.inventory
            inventory.adds(self._product_condition_cache["production"])
            self.production_timer = self._product_condition_cache["time"]
            self.deposit_capacity -= 1
            self.make_dirty()

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
            "deposit_capacity": self.deposit_capacity
        }
