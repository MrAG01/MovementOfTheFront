import arcade

from GUI.ui_title_setter_layout import UITitleSetterLayout
from core.callback import Callback
from game.game_manager import GameManager
from game.game_state import ServerGameState
from game.map.server_map import ServerMap
from network.server.game_server_config import GameServerConfig
from network.server_logger.server_logger_manager import ServerLoggerManager
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from arcade.gui import UIManager, UIBoxLayout, UIAnchorLayout, UISlider, UILabel, UIInputText

from scenes.room_host_menu import RoomHostMenuView


class RoomGeneratorMenuView(arcade.View):
    def __init__(self, game_state: ServerGameState, view_setter, game_manager, back_menu, resource_manager,
                 mods_manager, server_logger_manager, config_manager, keyboard_manager, mouse_manager):
        super().__init__()
        self.game_state = game_state
        self.view_setter = view_setter
        self.game_manager: GameManager = game_manager
        self.back_menu = back_menu
        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager = mods_manager
        self.server_logger_manager = server_logger_manager
        self.config_manager = config_manager
        self.keyboard_manager = keyboard_manager
        self.mouse_manager = mouse_manager
        self.ui_manager = UIManager()

    def _on_create_room_button_pressed_(self, event):
        self.error_label.text = ""
        password_input_text = self.password_input.text
        password = None if password_input_text == "" else password_input_text
        max_players = self.max_players_slider.value
        server_name = self.server_name_input.text
        server_config = GameServerConfig(server_name, max_players, password)
        callback: Callback = self.game_manager.create_new_multiplayer_room(self.game_state, server_config,
                                                                           self.server_logger_manager)
        if callback.is_error():
            self.error_label.text = callback.message
            return
        self.view_setter(
            RoomHostMenuView(self.view_setter, self.game_manager, self.back_menu, self.resource_manager,
                             self.mods_manager, self.config_manager, self.keyboard_manager, self.mouse_manager))

    def _on_back_button_clicked_(self, event):
        self.view_setter(self.back_menu)

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        background_widget = self.resource_manager.create_widget("main_menu_background")
        layout = UIBoxLayout(vertical=True, align="center", space_between=10, size_hint=(0.7, 0.5))

        self.server_name_input = self.resource_manager.create_widget("server_name_input")
        self.server_name_input.text = "My server"
        self.password_input = self.resource_manager.create_widget("password_input")
        self.password_input.text = ""
        self.max_players_slider = self.resource_manager.create_widget("max_players_slider")

        create_room_button = self.resource_manager.create_widget("room_generator_create_room_button")
        create_room_button.on_click = self._on_create_room_button_pressed_

        back_button = self.resource_manager.create_widget("back_button")
        back_button.on_click = self._on_back_button_clicked_

        self.error_label = UILabel(size_hint=(1.0, 1.0), text_color=[255, 0, 0])
        self.error_label.text = ""
        layout.add(self.error_label)
        layout.add(
            UITitleSetterLayout(self.resource_manager.create_widget("server_name_helper_label"),
                                self.server_name_input,
                                vertical=False, size_hint=(1, 1)))
        layout.add(
            UITitleSetterLayout(self.resource_manager.create_widget("password_input_helper_label"),
                                self.password_input,
                                vertical=False, size_hint=(1, 1)))
        layout.add(UITitleSetterLayout(self.resource_manager.create_widget("max_players_helper_label"),
                                       self.max_players_slider,
                                       vertical=False, size_hint=(1, 1)))

        layout.add(create_room_button)
        layout.add(back_button)

        anchor = UIAnchorLayout()
        anchor.add(child=background_widget, anchor_x="center_x", anchor_y="center_y")
        anchor.add(child=layout, anchor_x="center_x", anchor_y="center_y")

        self.ui_manager.add(anchor)

    def on_show_view(self) -> None:
        self.setup_gui()

    def on_hide_view(self):
        self.ui_manager.disable()

    def on_draw(self):
        self.clear()
        self.ui_manager.draw()

    def on_update(self, delta_time):
        self.ui_manager.on_update(delta_time)
