import random

import arcade
from arcade.gui import UIManager, UIBoxLayout, UIAnchorLayout, UILabel

from GUI.ui_title_setter_layout import UITitleSetterLayout
from game.game_state.server_game_state import ServerGameState
from game.map.map_generation_settings import MapGenerationSettings
from game.map.map_generator import MapGenerator
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from scenes.room_generator_menu_view import RoomGeneratorMenuView


class WorldGeneratorMenuView(arcade.View):
    def __init__(self, view_setter, back_menu, resource_manager, mods_manager, server_logger_manager,
                 config_manager, keyboard_manager, mouse_manager):
        super().__init__()
        self.view_setter = view_setter
        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager = mods_manager
        self.server_logger_manager = server_logger_manager
        self.back_menu = back_menu
        self.config_manager = config_manager
        self.keyboard_manager = keyboard_manager
        self.mouse_manager = mouse_manager
        self.ui_manager = UIManager()

    def _get_map_generation_settings(self):
        try:
            seed = int(self.seed_input.text)
            width = int(self.width_input.text)
            height = int(self.height_input.text)
        except ValueError:
            return {"success": False, "error": "Invalid seed"}
        map_generator = MapGenerationSettings(seed, width=width, height=height)
        return {"success": True, "data": map_generator}

    def _on_create_room_clicked_(self, *args):
        #self.error_label.text = ""
        return_data = self._get_map_generation_settings()
        if return_data["success"]:
            map_generator = MapGenerator(return_data["data"], self.resource_manager, self.mods_manager)
            self.view_setter(
                RoomGeneratorMenuView(map_generator, self.view_setter, self,
                                      self.resource_manager,
                                      self.mods_manager, self.server_logger_manager, self.config_manager,
                                      self.keyboard_manager, self.mouse_manager))
        #else:
            #self.error_label.text = return_data["error"]

    def _on_play_single_player_clicked_(self, *args):
        #self.error_label.text = ""
        return_data = self._get_map_generation_settings()
        if return_data["success"]:
            generator = MapGenerator(return_data["data"], self.resource_manager, self.mods_manager)
        #else:
            #self.error_label.text = return_data["error"]

    def _on_back_button_clicked_(self, *args):
        self.view_setter(self.back_menu)

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        #self.error_label = UILabel(size_hint=(1.0, 1.0), font_name=self.resource_manager.get_default_font(),
        #                           font_size=16, text_color=[255, 0, 0])

        self.seed_input = self.resource_manager.create_widget("seed_input")
        self.seed_input.text = str(random.randint(1_000_000, 9_999_999))

        self.width_input = self.resource_manager.create_widget("width_input")
        self.width_input.text = str(800)

        self.height_input = self.resource_manager.create_widget("height_input")
        self.height_input.text = str(800)

        layout2 = UIBoxLayout(vertical=False, align="center", space_between=5, size_hint=(1.0, 1.0))

        create_room = self.resource_manager.create_widget("world_generator_create_room")
        create_room.on_click = self._on_create_room_clicked_

        play_single_player = self.resource_manager.create_widget("play_single_player")
        play_single_player.on_click = self._on_play_single_player_clicked_

        layout2.add(create_room)
        layout2.add(play_single_player)

        back_button = self.resource_manager.create_widget("back_button")
        back_button.on_click = self._on_back_button_clicked_
        menu_background = self.resource_manager.create_widget("menus_background", size_hint=(0.9, 0.75))
        background_widget = self.resource_manager.create_widget("main_menu_background")
        layout = UIBoxLayout(vertical=True, align="center", space_between=5, size_hint=(0.7, 0.4))

        #layout.add(self.error_label)

        layout.add(
            UITitleSetterLayout(self.resource_manager.create_widget("width_input_helper_label"), self.width_input,
                                size_hint=(1, 1), vertical=False))
        layout.add(
            UITitleSetterLayout(self.resource_manager.create_widget("height_input_helper_label"), self.height_input,
                                size_hint=(1, 1), vertical=False))

        layout.add(UITitleSetterLayout(self.resource_manager.create_widget("seed_input_helper_label"), self.seed_input,
                                       size_hint=(1, 1), vertical=False))
        layout.add(layout2)
        layout.add(back_button)

        anchor = UIAnchorLayout()
        anchor.add(child=background_widget, anchor_x="center_x", anchor_y="center_y")
        anchor.add(child=menu_background, anchor_x="center_x", anchor_y="center_y")
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
