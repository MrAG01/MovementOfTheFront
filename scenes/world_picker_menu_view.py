import arcade
from arcade.gui import UIManager, UIBoxLayout, UIAnchorLayout

from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from scenes.world_generator_menu_view import WorldGeneratorMenuView


class WorldPickerMenuView(arcade.View):
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

    def _on_generate_new_world_button_clicked_(self, *args):
        self.view_setter(
            WorldGeneratorMenuView(self.view_setter, self, self.resource_manager, self.mods_manager,
                                   self.server_logger_manager, self.config_manager, self.keyboard_manager, self.mouse_manager))

    def _on_load_world_button_clicked_(self, *args):
        print("LOAD_WORLD")

    def _on_back_button_clicked_(self, *args):
        self.view_setter(self.back_menu)

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        generate_new_world_button = self.resource_manager.create_widget("generate_new_world_button")
        generate_new_world_button.on_click = self._on_generate_new_world_button_clicked_

        load_world_button = self.resource_manager.create_widget("load_world_button")
        load_world_button.on_click = self._on_load_world_button_clicked_

        back_button = self.resource_manager.create_widget("back_button")
        back_button.on_click = self._on_back_button_clicked_

        menu_background = self.resource_manager.create_widget("menus_background", size_hint=(0.9, 0.7))
        background_widget = self.resource_manager.create_widget("main_menu_background")
        layout = UIBoxLayout(vertical=True, align="center", space_between=5, size_hint=(0.7, 0.3))

        layout.add(generate_new_world_button)
        layout.add(load_world_button)
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
