import arcade

from configs.window_config import WindowConfig
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from arcade.gui import UIManager, UIBoxLayout, UIAnchorLayout
from scenes.multi_player_menu_view import MultiplayerMenuView
from scenes.resource_packs_menu_view import ResourcePacksMenuView
from scenes.settings_menu_view import UISettingsMenu
from scenes.world_generator_menu_view import WorldGeneratorMenuView


class MainMenuView(arcade.View):
    def __init__(self, view_setter, resource_manager, mods_manager, server_logger_manager,
                 config_manager, keyboard_manager, mouse_manager):
        super().__init__()
        self.view_setter = view_setter
        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager = mods_manager
        self.server_logger_manager = server_logger_manager
        self.config_manager = config_manager
        self.keyboard_manager = keyboard_manager
        self.mouse_manager = mouse_manager
        self.ui_manager = UIManager()

    def _on_play_button_clicked_(self, event):
        self.view_setter(
            WorldGeneratorMenuView(self.view_setter, self, self.resource_manager, self.mods_manager,
                                   self.server_logger_manager, self.config_manager, self.keyboard_manager,
                                   self.mouse_manager))

    def _on_multi_player_button_clicked_(self, event):
        self.view_setter(
            MultiplayerMenuView(self.view_setter, self, self.resource_manager, self.mods_manager,
                                self.server_logger_manager, self.config_manager, self.keyboard_manager,
                                self.mouse_manager))

    def _on_mods_button_clicked_(self, event):
        print("MODS")

    def _on_resource_packs_button_clicked_(self, event):
        self.view_setter(ResourcePacksMenuView(self.view_setter, self, self.resource_manager))

    def _on_settings_button_clicked_(self, event):
        self.view_setter(UISettingsMenu(self.view_setter, self, self.config_manager, self.resource_manager))

    def _on_exit_button_clicked_(self, event):
        arcade.exit()

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        play_button = self.resource_manager.create_widget("play_button")
        play_button.set_callback(self._on_play_button_clicked_)

        multi_player_button = self.resource_manager.create_widget("multi_player_button")
        multi_player_button.set_callback(self._on_multi_player_button_clicked_)

        # mods_button = self.resource_manager.create_widget("mods_button")
        # mods_button.on_click = self._on_mods_button_clicked_

        resource_packs_button = self.resource_manager.create_widget("resource_packs_button")
        resource_packs_button.set_callback(self._on_resource_packs_button_clicked_)

        settings_button = self.resource_manager.create_widget("settings_button")
        settings_button.set_callback(self._on_settings_button_clicked_)

        exit_button = self.resource_manager.create_widget("exit_button")
        exit_button.set_callback(self._on_exit_button_clicked_)

        background_widget = self.resource_manager.create_widget("main_menu_background")

        menu_background = self.resource_manager.create_widget("menus_background", size_hint=(0.75, 0.55))
        layout = UIBoxLayout(vertical=True, align="center", space_between=5, size_hint=(0.7, 0.5))

        layout.add(play_button)
        layout.add(multi_player_button)

        layout.add(resource_packs_button)
        layout.add(settings_button)
        layout.add(exit_button)

        anchor = UIAnchorLayout()
        anchor.add(child=background_widget, anchor_x="center_x", anchor_y="center_y")
        anchor.add(child=menu_background, anchor_x="center_x", anchor_y="center_y")
        anchor.add(child=layout, anchor_x="center_x", anchor_y="center_y")

        self.ui_manager.add(anchor)

    def on_show_view(self) -> None:
        self.setup_gui()
        window_config: WindowConfig = self.config_manager.register_config("window_config", WindowConfig)
        self.ui_manager.on_resize(window_config.window_width, window_config.window_height)

    def on_hide_view(self):
        self.ui_manager.disable()

    def on_draw(self):
        self.clear()
        self.ui_manager.draw()

    def on_update(self, delta_time):
        self.ui_manager.on_update(delta_time)
