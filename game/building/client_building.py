import arcade.color

from GUI.ui_objects_progress_bar import UIObjectsProgressBar
from components.items import Items
from game.actions.events import Event, BuildingEvents
from game.building.building_config import BuildingConfig
from game.building.building_state import BuildingState
from game.building.production.production_rule import ProductionRule
from game.camera import Camera
from game.deposits.deposit_config import DepositConfig
from resources.handlers.texture_handle import TextureHandle
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from resources.mods.mods_manager.mods_manager import ModsManager
from arcade import Vec2


class ClientBuilding(arcade.Sprite):
    interpolation_speed = 1.0

    def __init__(self, server_snapshot: dict, resource_manager, mods_manager, team_color):
        super().__init__()
        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager: ModsManager = mods_manager
        self.color = team_color
        self.id = server_snapshot["id"]
        self.owner_id = server_snapshot["owner_id"]
        self.position = Vec2(*server_snapshot["position"])
        self.health = server_snapshot["health"]
        self.level = server_snapshot["level"]
        self.units_queue = server_snapshot["units_queue"]
        self.production_index = server_snapshot["production_index"]

        self.config: BuildingConfig = self.mods_manager.get_building(server_snapshot["config_name"])

        self.state = BuildingState(server_snapshot["state"])

        self.texture = self.resource_manager.get_texture(self.config.name).get()
        self.size = (self.config.size, self.config.size)

        self.outline_texture: TextureHandle = self.resource_manager.get_texture(self.config.outline_texture_name)

        self.selected = False
        self.linked_deposit_config = None

        self.outline_enabled = False
        self.setup_gui()
        self._apply_events([Event.from_dict(event_data) for event_data in server_snapshot["events"]])

        self.on_unit_queue_changed_callback = None

        self.on_move_callbacks = set()

    def get_production_rules(self):
        self_rules = self.config.production if self.config.production else []
        static_rule = None
        if self.linked_deposit_config:
            data = self.linked_deposit_config.product_buildings[self.config.name]
            self_items_product: Items = data["production"]
            static_rule = ProductionRule(data["time"], Items({}), self_items_product)

        return self_rules, static_rule

    def _notify_on_move_callback_listeners(self):
        for callback in self.on_move_callbacks:
            callback(self)

    def append_on_move_callback(self, callback):
        self.on_move_callbacks.add(callback)

    def remove_on_move_callback(self, callback):
        if callback in self.on_move_callbacks:
            self.on_move_callbacks.remove(callback)

    def set_on_unit_queue_changed_callback(self, callback):
        self.on_unit_queue_changed_callback = callback

    def reset_on_unit_queue_changed_callback(self):
        self.on_unit_queue_changed_callback = None

    def setup_gui(self):
        x, y = self.position
        r = self.config.size
        self.bars_step = r * 0.2
        self.progress_bar_slider = UIObjectsProgressBar(
            center_x=x,
            top_y=y,
            offset_height=-r / 2 - 0.2,
            width=r,
            height=r * 0.15,
            bg_color=arcade.color.Color(50, 50, 50),
            bar_color=arcade.color.Color(150, 150, 50),
            border_color=arcade.color.Color(0, 0, 0)
        )
        if self.config.can_spawn_units:
            self.units_production_state_progress_bar = UIObjectsProgressBar(
                center_x=x,
                top_y=y,
                offset_height=-r / 2 - 0.2,
                width=r,
                height=r * 0.15,
                bg_color=arcade.color.Color(50, 50, 50),
                bar_color=arcade.color.Color(150, 50, 50),
                border_color=arcade.color.Color(0, 0, 0)
            )
        else:
            self.units_production_state_progress_bar = None

        self.building_state_progress_bar = UIObjectsProgressBar(
            center_x=x,
            top_y=y,
            offset_height=-r / 2 - 0.2,
            width=r,
            height=r * 0.15,
            bg_color=arcade.color.Color(50, 50, 50),
            bar_color=arcade.color.Color(50, 50, 150),
            border_color=arcade.color.Color(0, 0, 0)
        )

        self.health_state_progress_bar = UIObjectsProgressBar(
            center_x=x,
            top_y=y,
            offset_height=-r / 2 - 0.2,
            width=r,
            height=r * 0.15,
            bg_color=arcade.color.Color(50, 50, 50),
            bar_color=arcade.color.Color(50, 150, 50),
            border_color=arcade.color.Color(0, 0, 0)
        )
        self.health_state_progress_bar.start(self.config.max_health)

    def enable_selection(self):
        self.selected = True

    def disable_selection(self):
        self.selected = False

    def enable_outline(self):
        if not self.selected:
            self.outline_enabled = True

    def disable_outline(self):
        self.outline_enabled = False

    def update_from_snapshot(self, snapshot):
        self.owner_id = snapshot["owner_id"]
        self.health = snapshot["health"]
        self.health_state_progress_bar.set_state(self.health)
        self.state = BuildingState(snapshot["state"])
        self.level = snapshot["level"]
        self.units_queue = snapshot["units_queue"]
        self.production_index = snapshot["production_index"]
        self._apply_events([Event.from_dict(event_data) for event_data in snapshot["events"]])

    def update_visual(self, delta_time):
        self.progress_bar_slider.on_update(delta_time)
        if self.units_production_state_progress_bar:
            self.units_production_state_progress_bar.on_update(delta_time)
        if self.state == BuildingState.BUILDING:
            self.building_state_progress_bar.on_update(delta_time)

    def get_damage(self, damage):
        self.health -= damage

    def _apply_events(self, events: list[Event]):
        for event in events:
            if event.event_type == BuildingEvents.BUILDING_START_BUILDING.value:
                self.building_state_progress_bar.start(event.data["build_time"])
            elif event.event_type == BuildingEvents.BUILDING_END_BUILDING.value:
                self.building_state_progress_bar.stop()
            elif event.event_type == BuildingEvents.PRODUCTION_STARTED.value:
                self.progress_bar_slider.start(event.data["time"])
            elif event.event_type == BuildingEvents.PRODUCTION_STOPPED.value:
                self.progress_bar_slider.stop()
            elif event.event_type == BuildingEvents.PRODUCTION_CONTINUE.value:
                self.progress_bar_slider.continue_()
            elif event.event_type == BuildingEvents.UNIT_ADD_IN_QUEUE.value:
                if self.on_unit_queue_changed_callback:
                    self.on_unit_queue_changed_callback()
            elif event.event_type == BuildingEvents.UNIT_REMOVE_FROM_QUEUE.value:
                if self.on_unit_queue_changed_callback:
                    self.on_unit_queue_changed_callback()
            elif event.event_type == BuildingEvents.UNIT_PRODUCTION_STARTED.value:
                if self.units_production_state_progress_bar:
                    self.units_production_state_progress_bar.start(event.data["time"])
            elif event.event_type == BuildingEvents.DEPOSIT_ATTACHED.value:
                self.linked_deposit_config = self.mods_manager.get_deposit(event.data)

    def draw_non_static(self, camera: Camera, alpha):
        zoom_k = self.config.size / self.texture.width
        outline_scale = zoom_k * 1.1

        if self.state == BuildingState.IDLE:
            if self.selected:
                self.outline_texture.draw(
                    self.position.x,
                    self.position.y,
                    outline_scale,
                    outline_scale,
                    color=arcade.color.Color(196, 196, 196, alpha)
                )
            elif self.outline_enabled:
                self.outline_texture.draw(
                    self.position.x,
                    self.position.y,
                    outline_scale,
                    outline_scale,
                    color=arcade.color.Color(128, 128, 128, alpha)
                )

            y_offset = 0
            if self.health != self.config.max_health:
                self.health_state_progress_bar.on_draw(camera, y_offset)
                y_offset += self.bars_step
            if self.units_production_state_progress_bar:
                if self.units_production_state_progress_bar.working:
                    self.units_production_state_progress_bar.on_draw(camera, y_offset)
                    y_offset += self.bars_step
            self.progress_bar_slider.on_draw(camera, y_offset)

            if self.building_state_progress_bar:
                self.building_state_progress_bar = None
        elif self.state == BuildingState.BUILDING:
            self.building_state_progress_bar.on_draw(camera, 0)
