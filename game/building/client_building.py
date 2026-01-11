from game.building.building_config import BuildingConfig
from game.building.building_state import BuildingState
from game.camera import Camera
from resources.handlers.texture_handle import TextureHandle
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from resources.mods.mods_manager.mods_manager import ModsManager
from arcade.math import lerp
from arcade import Vec2


class ClientBuilding:
    interpolation_speed = 1.0

    def __init__(self, server_snapshot: dict, resource_manager, mods_manager):
        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager: ModsManager = mods_manager
        self.id = server_snapshot["id"]
        self.owner_id = server_snapshot["owner_id"]
        self.position = Vec2(*server_snapshot["position"])
        self._target_health = self.health = server_snapshot["health"]
        self.level = server_snapshot["level"]

        self.config: BuildingConfig = self.mods_manager.get_building(server_snapshot["config_name"])

        self.state = BuildingState(server_snapshot["state"])
        self.building_progress = server_snapshot["building_progress"]

        self.texture: TextureHandle = self.resource_manager.get_texture(self.config.name)

        self._apply_events(server_snapshot["events"])

    def update_from_snapshot(self, snapshot):
        self.owner_id = snapshot["owner_id"]
        self._target_health = snapshot["health"]
        self.state = BuildingState(snapshot["state"])
        self.level = snapshot["level"]
        self.building_progress = snapshot["building_progress"]
        self._apply_events(snapshot["events"])

    def update_visual(self, delta_time):
        if self.health != self._target_health:
            self.health = lerp(self.health, self._target_health, min(self.interpolation_speed * delta_time, 1.0))

    def _apply_events(self, events: dict):
        pass

    def draw(self, camera: Camera):
        zoom_k = 1 / camera.zoom
        if self.state == BuildingState.IDLE:
            self.texture.draw(self.position.x, self.position.y, zoom_k, zoom_k)
        elif self.state == BuildingState.BUILDING:

            self.texture.draw(self.position.x, self.position.y, zoom_k, zoom_k,
                              alpha=255 * self.building_progress)
