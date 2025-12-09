from arcade import Vec2
from components.building.building_config import BuildingConfig
from resources.mods.mod_errors import ModLoadError
from resources.mods.mods_manager.mods_manager import ModsManager
from resources.resource_packs.resource_manager.resource_manager import ResourceManager


class BuildingAnimation:
    def __init__(self, delay, frame):
        self.frame_texture = frame
        self.delay = delay
        self.progress_time = 0
        self.finished = False

    def update(self, delta_time):
        if not self.finished:
            self.progress_time += delta_time
            if self.progress_time >= delta_time:
                self.finished = True

    def draw(self, x, y, scale=2.0):
        self.frame_texture.draw(x, y, scale, scale, alpha=int(255 * max(self.progress_time / self.delay, 1)),
                                pixelated=True)


class Building:
    def __init__(self, resource_manager: ResourceManager, mods_manager: ModsManager, building_name, position: Vec2):
        self.resource_manager = resource_manager
        self.mods_manager = mods_manager

        self.building_name = building_name
        self.config: BuildingConfig = mods_manager.get_building(building_name)
        if self.config is None:
            raise ModLoadError("???")

        self.base_texture = resource_manager.get_texture(self.config.base_texture_name)
        self.texture = resource_manager.get_texture(self.config.texture_name)

        self.position = position

        self.building_animation = BuildingAnimation(self.config.build_time, self.texture)
        self.building = True

    def serialize(self):
        return {
            "building_name": self.building_name,
            "position": list(self.position),
            "building": self.building
        }

    def is_building(self):
        return self.building

    def update(self, delta_time):
        if self.building:
            self.building_animation.update(delta_time)

    def draw(self):
        self.base_texture.draw(self.position.x, self.position.y)
        if self.building:
            self.building_animation.draw(self.position.x, self.position.y)
        else:
            self.texture.draw(self.position.x, self.position.y)
