from arcade import Vec2

from components.animation import Animation
from components.building.building_config import BuildingConfig
from resources.resource_packs.resource_manager.resource_manager import ResourceManager


class BuildingAnimation(Animation):
    def __init__(self, delay, final_frame):
        super().__init__([final_frame], 1 / delay)
        self.delay = delay

    def draw(self, x, y, scale=2.0):
        current_index = int(self.current_frame)
        next_index = (current_index + 1) % len(self.frames)
        progress = self.flag_time_counter / self.frame_duration
        current_texture = self.frames[current_index]
        next_texture = self.frames[next_index]

        if self.is_very_first_appearance and current_index == 0:
            current_texture.draw(x, y, scale, scale, alpha=int(255 * progress), pixelated=True)
            return
        if progress >= 0:
            current_texture.draw(x, y, scale, scale, pixelated=True)
        if progress <= 1:
            next_texture.draw(x, y, scale, scale, alpha=int(255 * progress), pixelated=True)


class Building:
    def __init__(self, resource_manager: ResourceManager, building_config, position: Vec2):
        self.config: BuildingConfig = building_config
        self.base_texture = resource_manager.get_texture(self.config.base_texture_name)
        self.texture = resource_manager.get_texture(self.config.texture_name)

        self.position = position

        self.building_animation = BuildingAnimation(self.config.build_time, self.texture)
        self.building = True

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
