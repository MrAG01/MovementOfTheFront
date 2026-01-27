import arcade
from GUI.players_scroll_view import PlayersScrollView
from game.game_mode import GameMode
from network.server.game_server import GameServer
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from arcade.gui import UIManager, UIBoxLayout, UIAnchorLayout

from scenes.game_view import GameView


class RoomHostMenuView(arcade.View):
    def __init__(self, view_setter, server, client, back_menu, resource_manager, mods_manager,
                 config_manager, keyboard_manager, mouse_manager):
        super().__init__()
        self.server = server
        self.client = client

        self.view_setter = view_setter
        self.back_menu = back_menu
        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager = mods_manager
        self.config_manager = config_manager
        self.keyboard_manager = keyboard_manager
        self.mouse_manager = mouse_manager
        self.ui_manager = UIManager()

    def _on_back_button_clicked_(self, event):
        self.server.shutdown()
        self.server = None
        self.client.disconnect()
        self.client = None
        self.view_setter(self.back_menu)

    def _on_start_game_button_pressed_(self, event):
        self.server.start_game(GameMode.FFA)
        self.view_setter(
            GameView(self.client, self.view_setter, self.back_menu, self.resource_manager, self.mods_manager,
                     self.config_manager, self.keyboard_manager, self.mouse_manager, self.server))
        self.client = None
        self.server = None

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        background_widget = self.resource_manager.create_widget("main_menu_background")
        menu_background = self.resource_manager.create_widget("menus_background", size_hint=(0.75, 0.55))
        layout = UIBoxLayout(vertical=True, align="center", space_between=10, size_hint=(0.7, 0.5))

        self.players_list_scroll_area = PlayersScrollView(self.resource_manager, self.client.get_clients_list(),
                                                          self.kick_player, self.ban_player, self.client.player_id,
                                                          size_hint=(1, 1))

        back_button = self.resource_manager.create_widget("back_button")
        back_button.size_hint = (1.0, 0.2)

        start_game_button = self.resource_manager.create_widget("start_game_button")
        start_game_button.set_callback(self._on_start_game_button_pressed_)

        back_button.set_callback(self._on_back_button_clicked_)
        layout.add(self.players_list_scroll_area)
        layout.add(start_game_button)
        layout.add(back_button)

        anchor = UIAnchorLayout()
        anchor.add(child=background_widget, anchor_x="center_x", anchor_y="center_y")
        anchor.add(child=menu_background, anchor_x="center_x", anchor_y="center_y")
        anchor.add(child=layout, anchor_x="center_x", anchor_y="center_y")

        self.ui_manager.add(anchor)

    def kick_player(self, player_data):
        self.server.kick_player(player_data[1])

    def ban_player(self, player_data):
        self.server.ban_player(player_data[1])

    def on_show_view(self) -> None:
        self.setup_gui()

    def on_hide_view(self):
        self.ui_manager.disable()

    def on_draw(self):
        self.clear()
        self.ui_manager.draw()

    def on_update(self, delta_time):
        self.ui_manager.on_update(delta_time)
        client_names = self.client.get_clients_list()
        self.players_list_scroll_area.update(client_names, self.client.player_id)
