import arcade
from arcade.gui import UIManager, UIBoxLayout, UIAnchorLayout

from GUI.ui_scroll_view import UIScrollView
from network.client.game_client import GameClient
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from scenes.game_view import GameView


class RoomClientMenuView(arcade.View):
    def __init__(self, view_setter, client, back_menu, resource_manager, mods_manager,
                 config_manager, keyboard_manager, mouse_manager):
        super().__init__()
        self.client: GameClient = client
        self.client.add_on_game_start_callback(self._on_game_start_wrapper)

        self.view_setter = view_setter
        self.back_menu = back_menu
        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager = mods_manager
        self.config_manager = config_manager
        self.keyboard_manager = keyboard_manager
        self.mouse_manager = mouse_manager
        self.ui_manager = UIManager()

    def _on_back_button_clicked_(self, event):
        self.view_setter(self.back_menu)

    def _on_game_start(self):
        self.view_setter(
            GameView(self.client, self.view_setter, self.back_menu, self.resource_manager, self.mods_manager,
                     self.config_manager, self.keyboard_manager, self.mouse_manager))

    def _on_game_start_wrapper(self):
        self.client.remove_on_game_start_callback(self._on_game_start_wrapper)
        arcade.schedule_once(lambda dt: self._on_game_start(), 0)

    def _on_new_player_joined(self):
        pass

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        background_widget = self.resource_manager.create_widget("main_menu_background")
        layout = UIBoxLayout(vertical=True, align="center", space_between=10, size_hint=(0.7, 0.5))

        self.players_list_scroll_area = UIScrollView(size_hint=(1, 1))

        back_button = self.resource_manager.create_widget("back_button")
        back_button.size_hint = (1.0, 0.2)

        back_button.on_clicked = self._on_back_button_clicked_
        layout.add(self.players_list_scroll_area)
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
