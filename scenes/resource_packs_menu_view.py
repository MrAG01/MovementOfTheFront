import os

import arcade
from arcade.gui import UIManager, UIBoxLayout, UIAnchorLayout

from GUI.ui_resource_pack_widget import UIResourcePackWidget
from resources.resource_packs.resource_manager.resource_manager import ResourceManager


class ResourcePacksMenuView(arcade.View):
    def __init__(self, view_setter, game_manager, main_menu_view, resource_manager):
        super().__init__()
        self.view_setter = view_setter
        self.game_manager = game_manager
        self.main_menu_view = main_menu_view
        self.resource_manager: ResourceManager = resource_manager

        self.available_packs = self.resource_manager.get_available_resource_packs_metadata()
        self.ui_manager = UIManager()

    def update_available_packs_list(self):
        self.available_packs = self.resource_manager.get_available_resource_packs_metadata()

    def _on_open_resource_packs_folder_button_clicked_(self, event):
        os.startfile(os.path.abspath(self.resource_manager.get_texture_packs_path()))

    def _on_back_button_clicked_(self, event):
        self.view_setter(self.main_menu_view)
    
    def _on_update_packs_list_button_clicked_(self, event):
        self.update_available_packs_list()

    def resource_packs_get_ordered(self):
        disabled_packs = []
        enabled_packs = []
        for pack in self.available_packs:
            if self.resource_manager.is_enabled(pack.name):
                enabled_packs.append(pack)
            else:
                disabled_packs.append(pack)
        return enabled_packs + disabled_packs

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()
        packs = self.resource_packs_get_ordered()

        base_vertical_layout = UIBoxLayout(vertical=True, align="center", size_hint=(0.8, 0.6))

        resource_packs_layout = UIBoxLayout(vertical=True, align="top", size_hint=(0.9, 0.8))
        for pack in packs:
            obj = UIResourcePackWidget(pack, size_hint=(1.0, 1.0))
            resource_packs_layout.add(obj)

        open_resource_packs_folder_button = self.resource_manager.create_widget("open_resource_packs_folder_button")
        open_resource_packs_folder_button.on_click = self._on_open_resource_packs_folder_button_clicked_

        back_button = self.resource_manager.create_widget("resource_packs_back_button")
        back_button.on_click = self._on_back_button_clicked_

        update_packs_list_button = self.resource_manager.create_widget("update_packs_list_button")
        update_packs_list_button.on_click = self._on_update_packs_list_button_clicked_

        buttons_horizontal_layout = UIBoxLayout(vertical=False, align="bottom", size_hint=(0.8, 0.4))
        buttons_horizontal_layout.add(back_button)
        buttons_horizontal_layout.add(update_packs_list_button)

        base_vertical_layout.add(resource_packs_layout)
        base_vertical_layout.add(open_resource_packs_folder_button)
        base_vertical_layout.add(buttons_horizontal_layout)


        print(packs[0].__dict__)
        p = UIResourcePackWidget(packs[0], size_hint=(0.5, 0.5))
        anchor = UIAnchorLayout()
        anchor.add(child=p, anchor_x="center_x", anchor_y="center_y")
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
