from tkinter.ttk import Label

import arcade

from GUI.ui_scroll_view import UIScrollView
from game.game_manager import GameManager
from game.map.map_generation_settings import MapGenerationSettings
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from arcade.gui import UIManager, UIBoxLayout, UIAnchorLayout, UILabel
from arcade.gui.experimental.scroll_area import UIScrollArea

from scenes.game_view import GameView


class RoomHostMenuView(arcade.View):
    def __init__(self, view_setter, game_manager, back_menu, resource_manager, mods_manager,
                 config_manager, keyboard_manager, mouse_manager):
        super().__init__()
        self.view_setter = view_setter
        self.game_manager: GameManager = game_manager
        self.back_menu = back_menu
        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager = mods_manager
        self.config_manager = config_manager
        self.keyboard_manager = keyboard_manager
        self.mouse_manager = mouse_manager
        self.ui_manager = UIManager()

    def _on_back_button_clicked_(self, event):
        self.view_setter(self.back_menu)

    def _on_start_game_button_pressed_(self, event):
        self.game_manager.start_game()
        self.view_setter(GameView(self.view_setter, self.game_manager, self.back_menu, self.resource_manager,
                                  self.config_manager, self.keyboard_manager, self.mouse_manager))

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        background_widget = self.resource_manager.create_widget("main_menu_background")
        layout = UIBoxLayout(vertical=True, align="center", space_between=10, size_hint=(0.7, 0.5))

        self.players_list_scroll_area = UIScrollView(size_hint=(1, 1))

        back_button = self.resource_manager.create_widget("back_button")
        back_button.size_hint = (1.0, 0.2)

        start_game_button = self.resource_manager.create_widget("start_game_button")
        start_game_button.on_click = self._on_start_game_button_pressed_

        back_button.on_clicked = self._on_back_button_clicked_
        layout.add(self.players_list_scroll_area)
        layout.add(start_game_button)
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
