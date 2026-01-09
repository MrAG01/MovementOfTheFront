import arcade
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from arcade.gui import UIManager, UIBoxLayout, UIAnchorLayout
from scenes.multi_player_menu_view import ViewRoomsView
from scenes.world_picker_menu_view import WorldPickerMenuView


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
            WorldPickerMenuView(self.view_setter, self, self.resource_manager, self.mods_manager,
                                self.server_logger_manager, self.config_manager, self.keyboard_manager,
                                self.mouse_manager))

    def _on_multi_player_button_clicked_(self, event):
        self.view_setter(
            ViewRoomsView(self.view_setter, self, self.resource_manager, self.mods_manager,
                          self.server_logger_manager, self.config_manager, self.keyboard_manager, self.mouse_manager))

    def _on_mods_button_clicked_(self, event):
        print("MODS")

    def _on_resource_packs_button_clicked_(self, event):
        # self.view_setter(ResourcePacksMenuView(self.view_setter, self.game_manager, self, self.resource_manager))
        pass

    def _on_settings_button_clicked_(self, event):
        print("SETTINGS")

    def _on_exit_button_clicked_(self, event):
        arcade.exit()

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        play_button = self.resource_manager.create_widget("play_button")
        play_button.on_click = self._on_play_button_clicked_

        multi_player_button = self.resource_manager.create_widget("multi_player_button")
        multi_player_button.on_click = self._on_multi_player_button_clicked_

        mods_button = self.resource_manager.create_widget("mods_button")
        mods_button.on_click = self._on_mods_button_clicked_

        resource_packs_button = self.resource_manager.create_widget("resource_packs_button")
        resource_packs_button.on_click = self._on_resource_packs_button_clicked_

        settings_button = self.resource_manager.create_widget("settings_button")
        settings_button.on_click = self._on_settings_button_clicked_

        exit_button = self.resource_manager.create_widget("exit_button")
        exit_button.on_click = self._on_exit_button_clicked_

        background_widget = self.resource_manager.create_widget("main_menu_background")
        layout = UIBoxLayout(vertical=True, align="center", space_between=5, size_hint=(0.7, 0.5))

        layout.add(play_button)
        layout.add(multi_player_button)
        layout.add(mods_button)
        layout.add(resource_packs_button)
        layout.add(settings_button)
        layout.add(exit_button)

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
