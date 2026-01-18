import arcade
import pyglet.window.mouse

from configs.base_config import BaseConfig


class CameraConfig(BaseConfig):
    def __init__(self, width_k=1.0, height_k=1.0, camera_speed=300, drag_sensitivity=0.2, min_zoom=0.1, max_zoom=3.0,
                 zoom_speed=0.1, invert_x=False, invert_y=False):
        self.width_k: float = width_k
        self.height_k: float = height_k
        self.camera_speed: float = camera_speed
        self.drag_sensitivity: float = drag_sensitivity
        self.zoom_speed: float = zoom_speed
        self.invert_x: bool = invert_x
        self.invert_y: bool = invert_y

    def serialize(self):
        return {
            "width_k": self.width_k,
            "height_k": self.height_k,
            "camera_speed": self.camera_speed,
            "drag_sensitivity": self.drag_sensitivity,
            "zoom_speed": self.zoom_speed,
            "invert_x": self.invert_x,
            "invert_y": self.invert_y
        }


class Camera(arcade.Camera2D):
    def __init__(self, config_manager, keyboard_manager, mouse_manager):
        self.config = config_manager.register_config("camera_config", CameraConfig)
        window_config = config_manager.get_config("window_config")
        if window_config is not None:
            width, height = window_config.resolution
        else:
            width, height = 1920, 1080

        self.keyboard_manager = keyboard_manager
        self.mouse_manager = mouse_manager

        super().__init__(viewport=arcade.rect.LBWH(0, 0, width, height))

        self.delta_time = 0

        window_config.add_listener(self.on_window_config_changed, notify_immediately=False)
        self._setup_key_binds()

    def screen_width(self):
        return self.viewport.width

    def screen_height(self):
        return self.viewport.height

    def on_window_config_changed(self, window_config):
        width, height = window_config.resolution
        self.viewport = arcade.rect.LBWH(0, 0, width, height)

        self._clamp_to_borders()

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

    def define_borders(self, width, height):
        self.border_width = width
        self.border_height = height
        self._clamp_to_borders()

    def _get_speed(self):
        return self.config.camera_speed / self.zoom

    def _move(self, arg: arcade.Vec2):
        self.position = self.position + arg
        self._clamp_to_borders()

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
        new_zoom = self.zoom + scroll_y * self.config.zoom_speed
        if old_zoom == new_zoom:
            return
        old_mp = self.unproject(arcade.Vec2(x, y))
        self.zoom = new_zoom
        new_mp = self.unproject(arcade.Vec2(x, y))
        offset = new_mp - old_mp
        self._move(-arcade.Vec2(offset.x, offset.y))

    def _handle_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.MIDDLE:
            direction_x = -1 * (-1 if self.config.invert_x else 1)
            direction_y = -1 * (-1 if self.config.invert_y else 1)
            self._move(arcade.Vec2(
                x=direction_x * dx * self.config.drag_sensitivity / self.zoom,
                y=direction_y * dy * self.config.drag_sensitivity / self.zoom
            ))
            self._clamp_to_borders()

    def update(self, delta_time):
        self.delta_time = delta_time

    def _clamp_to_borders(self):
        if not (hasattr(self, 'border_width') and hasattr(self, 'border_height')):
            return

        min_zoom_x = self.viewport.width / self.border_width
        min_zoom_y = self.viewport.height / self.border_height
        min_zoom = max(min_zoom_x, min_zoom_y)

        if self.zoom < min_zoom:
            self.zoom = min_zoom

        half_w = self.projection.width / 2
        half_h = self.projection.height / 2

        min_x = half_w
        max_x = self.border_width - half_w
        min_y = half_h
        max_y = self.border_height - half_h

        cur_x, cur_y = self.position

        if half_w * 2 >= self.border_width:
            new_x = self.border_width / 2
        else:
            new_x = max(min_x, min(cur_x, max_x))

        if half_h * 2 >= self.border_height:
            new_y = self.border_height / 2
        else:
            new_y = max(min_y, min(cur_y, max_y))

        self.position = (new_x, new_y)
