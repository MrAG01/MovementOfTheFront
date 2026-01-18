import arcade

from GUI.ui_objects_progress_bar import UIObjectsProgressBar
from game.actions.events import Event
from game.unit.unit_config import UnitConfig
from resources.handlers.texture_handle import TextureHandle


class ClientUnit:
    def __init__(self, snapshot, resource_manager, mods_manager):
        self.resource_manager = resource_manager
        self.mods_manager = mods_manager
        self.id = snapshot["id"]
        self.owner_id = snapshot["owner_id"]

        self.config: UnitConfig = mods_manager.get_unit(snapshot["unit_config_name"])

        self.hit_box_radius = snapshot["hit_box_radius"]

        self.health = snapshot["health"]
        self.position = arcade.Vec2(*snapshot["position"])

        self.texture: TextureHandle = self.resource_manager.get_texture(self.config.name)

        self.setup_gui()
        self._apply_events(snapshot["events"])

    def setup_gui(self):
        x, y = self.position
        w, h = self.texture.get_size()

        self.health_bar_slider = UIObjectsProgressBar(
            center_x=x,
            top_y=y,
            offset_height=-h / 2 - 4,
            width=w - 4,
            height=12,
            bg_color=arcade.color.Color(50, 50, 50),
            bar_color=arcade.color.Color(50, 150, 50),
            border_color=arcade.color.Color(0, 0, 0)
        )
        self.health_bar_slider.start(self.config.max_health)

    def _apply_events(self, events: list[Event]):
        pass

    def update_from_snapshot(self, snapshot):
        self.health = snapshot["health"]
        self.health_bar_slider.set_state(self.health)

        self.position = arcade.Vec2(*snapshot["position"])
        self._apply_events(snapshot["events"])

    def draw(self, team_color, camera):
        w, h = self.texture.get_size()

        k = (self.config.texture_radius * 2) / w

        self.texture.draw(self.position.x, self.position.y, color=team_color, scale_x=k, scale_y=k)
        if self.health != self.config.max_health:
            self.health_bar_slider.on_draw(camera, 0)
