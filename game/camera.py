import arcade
import pyglet.window.mouse

from configs.base_config import BaseConfig
from resources.input.keyboard_manager import KeyboardManager
from resources.input.mouse_manager import MouseManager


class CameraConfig(BaseConfig):
    width_k: float = 1.0
    height_k: float = 1.0
    camera_speed: float = 300
    drag_sensitivity: float = 0.2
    min_zoom: float = 0.1
    max_zoom: float = 3.0
    zoom_speed: float = 0.1
    invert_x: bool = False
    invert_y: bool = False

    def serialize(self):
        return {
            "width_k": self.width_k,
            "height_k": self.height_k,
            "camera_speed": self.camera_speed,
            "drag_sensitivity": self.drag_sensitivity,
            "min_zoom": self.min_zoom,
            "max_zoom": self.max_zoom,
            "zoom_speed": self.zoom_speed,
            "invert_x": self.invert_x,
            "invert_y": self.invert_y
        }



class Camera(arcade.Camera2D):
    def __init__(self, config_manager, keyboard_manager, mouse_manager, width, height):
        self.config = config_manager.register_config("camera_config", CameraConfig)
        self.keyboard_manager: KeyboardManager = keyboard_manager
        self.mouse_manager: MouseManager = mouse_manager
        super().__init__(
            viewport=arcade.rect.LBWH(0, 0, width, height),
            projection=arcade.rect.LBWH(0, 0, width * self.config.width_k, height * self.config.height_k)
        )
        self.delta_time = 0
        self._setup_key_binds()

    def _setup_key_binds(self):
        self.keyboard_manager.register_callback("move_camera_left",
                                                on_holding_callback=self.move_left)
        self.keyboard_manager.register_callback("move_camera_right",
                                                on_holding_callback=self.move_right)
        self.keyboard_manager.register_callback("move_camera_up",
                                                on_holding_callback=self.move_up)
        self.keyboard_manager.register_callback("move_camera_down",
                                                on_holding_callback=self.move_down)
        self.mouse_manager.register_on_scroll_callback(self._handle_mouse_scroll)
        self.mouse_manager.register_on_dragging_callback(self._handle_mouse_drag)

    def _get_speed(self):
        return self.config.camera_speed / self.zoom

    def _move(self, arg: arcade.Vec2):
        self.position = self.position + arg

    def move_left(self):
        direction = -1 * (-1 if self.config.invert_x else 1)
        self._move(arcade.Vec2(direction * self._get_speed() * self.delta_time, 0))

    def move_right(self):
        direction = 1 * (-1 if self.config.invert_x else 1)
        self._move(arcade.Vec2(direction * self._get_speed() * self.delta_time, 0))

    def move_up(self):
        direction = 1 * (-1 if self.config.invert_y else 1)
        self._move(arcade.Vec2(0, direction * self._get_speed() * self.delta_time))

    def move_down(self):
        direction = -1 * (-1 if self.config.invert_y else 1)
        self._move(arcade.Vec2(0, direction * self._get_speed() * self.delta_time))

    def _handle_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y == 0:
            return

        old_zoom = self.zoom
        new_zoom = max(min(self.zoom + scroll_y * self.config.zoom_speed, self.config.max_zoom), self.config.min_zoom)

        if old_zoom == new_zoom:
            return

        old_mp = self.unproject(arcade.Vec2(x, y))
        self.zoom = new_zoom
        new_mp = self.unproject(arcade.Vec2(x, y))
        offset = new_mp - old_mp
        self._move(-arcade.Vec2(offset.x, offset.y))

    def _handle_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        direction_x = -1 * (-1 if self.config.invert_x else 1)
        direction_y = -1 * (-1 if self.config.invert_y else 1)
        if buttons & pyglet.window.mouse.LEFT:
            self._move(arcade.Vec2(
                x=direction_x * self._get_speed() * dx * self.delta_time * self.config.drag_sensitivity,
                y=direction_y * self._get_speed() * dy * self.delta_time * self.config.drag_sensitivity
            ))

    def update(self, delta_time):
        self.delta_time = delta_time
