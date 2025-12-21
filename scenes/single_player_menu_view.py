import arcade
from arcade.gui import UIManager, UIBoxLayout, UIAnchorLayout

from resources.resource_packs.resource_manager.resource_manager import ResourceManager


class SinglePlayerMenuView(arcade.View):
    def __init__(self, view_setter, main_menu_view, resource_manager):
        super().__init__()
        self.view_setter = view_setter
        self.main_menu_view = main_menu_view
        self.resource_manager: ResourceManager = resource_manager
        self.ui_manager = UIManager()

    def _on_single_player_create_new_button_clicked_(self, event):
        print("SINGLEPLAYER_CREATE_NEW")

    def _on_single_player_load_button_clicked_(self, event):
        print("SINGLEPLAYER_LOAD_FROM")

    def _on_back_button_clicked_(self, event):
        self.view_setter(self.main_menu_view)

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        single_player_create_new_button = self.resource_manager.create_widget("single_player_create_new_button")
        single_player_create_new_button.on_click = self._on_single_player_create_new_button_clicked_

        single_player_load_button = self.resource_manager.create_widget("single_player_load_button")
        single_player_load_button.on_click = self._on_single_player_load_button_clicked_

        back_button = self.resource_manager.create_widget("back_button")
        back_button.on_click = self._on_back_button_clicked_

        layout = UIBoxLayout(vertical=True, align="center", space_between=10)
        layout.add(single_player_create_new_button)
        layout.add(single_player_load_button)
        layout.add(back_button)

        anchor = UIAnchorLayout()
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
