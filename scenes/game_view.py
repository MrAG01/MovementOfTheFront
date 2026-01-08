import arcade
from arcade.gui import UIManager

from game.camera import Camera
from game.game_manager import GameManager
from resources.resource_packs.resource_manager.resource_manager import ResourceManager


class GameView(arcade.View):
    def __init__(self, view_setter, game_manager, back_menu, resource_manager,
                 config_manager, keyboard_manager, mouse_manager):
        super().__init__()
        self.view_setter = view_setter
        self.game_manager: GameManager = game_manager
        self.back_menu = back_menu
        self.resource_manager: ResourceManager = resource_manager
        self.keyboard_manager = keyboard_manager
        self.main_camera = Camera(config_manager, keyboard_manager, mouse_manager)
        self.ui_manager = UIManager()

        self.pause = False
        self._setup_key_binds()

    def _setup_key_binds(self):
        self.keyboard_manager.register_callback("pause",
                                                on_pressed_callback=self._on_pause_button_pressed_)

    def setup_gui(self):
        self.ui_manager.clear()

    def on_show_view(self) -> None:
        self.setup_gui()

    def _on_pause_button_pressed_(self):
        if self.pause:
            self.ui_manager.disable()
            self.pause = False
        else:
            self.ui_manager.enable()
            self.pause = True

    def on_hide_view(self):
        self.ui_manager.disable()

    def on_draw(self):
        self.clear()
        self.main_camera.use()
        self.game_manager.apply_camera(self.main_camera)
        self.game_manager.draw()

        self.ui_manager.draw()

    def on_update(self, delta_time):
        self.ui_manager.on_update(delta_time)
        self.main_camera.update(delta_time)
