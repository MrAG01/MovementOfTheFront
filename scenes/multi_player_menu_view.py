import arcade

from game.game_manager import GameManager
from game.map.map_generation_settings import MapGenerationSettings
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from arcade.gui import UIManager, UIBoxLayout, UIAnchorLayout
from arcade.gui import (
    UIFlatButton
)


class MultiPlayerMenuView(arcade.View):
    def __init__(self, view_setter, game_manager, main_menu_view, resource_manager, mods_manager):
        super().__init__()
        self.view_setter = view_setter
        self.game_manager: GameManager = game_manager
        self.main_menu_view = main_menu_view
        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager = mods_manager
        self.ui_manager = UIManager()

    def _on_create_room_button_clicked_(self, event):
        self.game_manager.create_new_multiplayer_room(MapGenerationSettings(width=400, height=400),
                                                      self.resource_manager, self.mods_manager)

    def _on_join_room_button_clicked_(self, event):
        print("JOIN_ROOM")

    def _on_viewing_rooms_clicked_(self, event):
        print("VIEWING_ROOMS")

    def _on_back_button_clicked_(self, event):
        self.view_setter(self.main_menu_view)

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        create_room_button = self.resource_manager.create_widget("create_room_button")
        create_room_button.on_click = self._on_create_room_button_clicked_

        join_room_button = self.resource_manager.create_widget("join_room_button")
        join_room_button.on_click = self._on_join_room_button_clicked_

        viewing_rooms_button = self.resource_manager.create_widget("viewing_rooms_button")
        viewing_rooms_button.on_click = self._on_viewing_rooms_clicked_

        back_button = self.resource_manager.create_widget("back_button")
        back_button.on_click = self._on_back_button_clicked_

        layout = UIBoxLayout(vertical=True, align="center", space_between=10)
        layout.add(create_room_button)
        layout.add(join_room_button)
        layout.add(viewing_rooms_button)
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
