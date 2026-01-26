from threading import Thread

import arcade

from GUI.ui_title_setter_layout import UITitleSetterLayout
from game.game_state.server_game_state import ServerGameState
from game.map.map_generation_settings import MapGenerationSettings
from game.map.map_generator import MapGenerator
from network.client.game_client import GameClient
from network.server.game_server import GameServer
from network.server.game_server_config import GameServerConfig
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from arcade.gui import UIManager, UIBoxLayout, UIAnchorLayout, UILabel

from scenes.loading_scene_view import LoadingView
from scenes.room_host_menu import RoomHostMenuView
from utils.os_utils import get_local_ip


class RoomGeneratorMenuView(arcade.View):

    def __init__(self, map_generator: MapGenerator, view_setter, back_menu, resource_manager,
                 mods_manager, server_logger_manager, config_manager, keyboard_manager, mouse_manager):
        super().__init__()
        self.map_generator = map_generator
        self.view_setter = view_setter
        self.back_menu = back_menu
        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager = mods_manager
        self.server_logger_manager = server_logger_manager
        self.config_manager = config_manager
        self.keyboard_manager = keyboard_manager
        self.mouse_manager = mouse_manager
        self.ui_manager = UIManager()

        self._loading_progress = 0.0
        self._loading_state = "Loading..."

    def _finish_room_creation(self, server, client):
        self.view_setter(
            RoomHostMenuView(self.view_setter, server, client, self.back_menu, self.resource_manager,
                             self.mods_manager, self.config_manager, self.keyboard_manager, self.mouse_manager))

    def _get_loading_progress(self):
        self._loading_progress += 0.02
        if self._loading_progress >= 0.99:
            self._loading_progress = 0.99
        return self._loading_state, self._loading_progress

    def _create_room_async(self, server_name, max_players, password):
        self._loading_state = self.resource_manager.get_located_text("loading_state_server_config", "text")
        server_config = GameServerConfig(server_name, max_players, password)

        self._loading_progress = 0.1
        self._loading_state = self.resource_manager.get_located_text("creating_game_state", "text")
        server_game_state = ServerGameState(self.mods_manager, self.map_generator.generate())

        self._loading_progress = 0.6
        self._loading_state = self.resource_manager.get_located_text("creating_server", "text")
        server = GameServer(get_local_ip(), server_config, server_game_state, self.server_logger_manager)
        callback = server.start()
        self._loading_state = self.resource_manager.get_located_text("close_to_ready", "text")
        self._loading_progress = 0.8
        #print(callback)
        if not callback.is_success():
            #self.error_label.text = callback.message
            return

        client = GameClient(self.config_manager, self.resource_manager, self.mods_manager, self.keyboard_manager,
                            self.mouse_manager)
        self._loading_progress = 0.9
        callback = client.connect(server.get_ip(), server.get_port(), password)
        #print(callback)
        if not callback.is_success():
            #self.error_label.text = callback.message
            return

        arcade.schedule_once(lambda *args: self._finish_room_creation(server, client), 0)


    def _on_create_room_button_pressed_(self, event):
        self.error_label.text = ""
        password_input_text = self.password_input.text
        password = None if password_input_text == "" else password_input_text
        max_players = self.max_players_slider.value
        server_name = self.server_name_input.text

        loading_view = LoadingView(
            resource_manager=self.resource_manager,
            return_callback=self._finish_room_creation,
            loading_progress_function=self._get_loading_progress,
            args=(server_name, max_players, password)
        )

        thread = Thread(target=self._create_room_async,
                        args=(server_name, max_players, password), daemon=True)
        self.view_setter(loading_view)
        thread.start()


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

        menu_background = self.resource_manager.create_widget("menus_background", size_hint=(0.9, 0.73))
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
        anchor.add(child=menu_background, anchor_x="center_x", anchor_y="center_y", align_y=-25)
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
