import os
import random

import arcade
from arcade.gui import UIManager, UIBoxLayout, UIAnchorLayout

from GUI.ui_resource_pack_widget import UIResourcePackWidget
from GUI.ui_scroll_view import UIScrollView
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from resources.resource_packs.resource_pack_meta_data import ResourcePackMetaData


class ResourcePacksMenuView(arcade.View):
    def __init__(self, view_setter, main_menu_view, resource_manager):
        super().__init__()
        self.view_setter = view_setter
        self.main_menu_view = main_menu_view
        self.resource_manager: ResourceManager = resource_manager

        self.enabled_packs = self.resource_manager.get_enabled_packs()
        self.disabled_packs = self.resource_manager.get_disabled_packs()
        self.ui_manager = UIManager()

    def _on_open_resource_packs_folder_button_clicked_(self, event):
        os.startfile(os.path.abspath(self.resource_manager.get_texture_packs_path()))

    def _on_back_button_clicked_(self, event):
        self.view_setter(self.main_menu_view)

    def _on_update_packs_list_button_clicked_(self, event):
        self.enabled_packs = self.resource_manager.get_enabled_packs()
        self.disabled_packs = self.resource_manager.get_disabled_packs()

    def _on_move_up_button_clicked(self, pack: ResourcePackMetaData):
        self.resource_manager.resource_manager_config.move_pack_up(pack.name)
        self.update_resource_packs()

    def _on_move_down_button_clicked(self, pack: ResourcePackMetaData):
        self.resource_manager.resource_manager_config.move_pack_down(pack.name)
        self.update_resource_packs()

    def _on_enable_pack_button_clicked(self, pack: ResourcePackMetaData):
        self.resource_manager.use_resource_pack(pack.name, -1)
        self.update_resource_packs()

    def _on_disable_pack_button_clicked_(self, pack: ResourcePackMetaData):
        self.resource_manager.disable_pack(pack.name)
        self.update_resource_packs()

    def update_resource_packs(self):
        self.disabled_resource_packs_layout.clear()
        self.enabled_resource_packs_layout.clear()

        self.enabled_packs = self.resource_manager.get_enabled_packs()
        self.disabled_packs = self.resource_manager.get_disabled_packs()

        for pack in self.enabled_packs:
            layout = UIBoxLayout(vertical=False, size_hint=(1, 1), space_between=5)
            buttons_layout = UIBoxLayout(size_hint=(0.5, 1), vertical=True, space_between=5)

            disable_pack_button = self.resource_manager.create_widget("disable_resource_pack_button")

            move_up_button = self.resource_manager.create_widget("move_resource_pack_up_button")
            move_down_button = self.resource_manager.create_widget("move_resource_pack_down_button")

            disable_pack_button.set_callback(lambda _, p=pack: self._on_disable_pack_button_clicked_(p))
            move_up_button.set_callback(lambda _, p=pack: self._on_move_up_button_clicked(p))
            move_down_button.set_callback(lambda _, p=pack: self._on_move_down_button_clicked(p))

            buttons_layout.add(move_up_button)
            buttons_layout.add(move_down_button)
            layout.add(disable_pack_button)
            layout.add(buttons_layout)

            obj = UIResourcePackWidget(self.resource_manager, pack, layout, ui_hint=(0.15, 1), size_hint=(1, None),
                                       height=85)
            self.enabled_resource_packs_layout.add(obj)

        for pack in self.disabled_packs:
            enable_button = self.resource_manager.create_widget("resource_pack_enable")

            enable_button.set_callback(lambda _, p=pack: self._on_enable_pack_button_clicked(p))

            obj = UIResourcePackWidget(self.resource_manager, pack, enable_button, size_hint=(1, None), height=85)
            self.disabled_resource_packs_layout.add(obj)

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        background = self.resource_manager.create_widget("main_menu_background")

        menu_background = self.resource_manager.create_widget("menus_background", size_hint=(0.75, 0.55))

        base_vertical_layout = UIBoxLayout(vertical=True, align="center", size_hint=(0.7, 0.5), space_between=5)
        resource_packs_scrolls_views_layout = UIBoxLayout(vertical=False, size_hint=(1, 1), space_between=5)

        self.enabled_resource_packs_layout = UIScrollView(vertical=True, size_hint=(1, 1))
        self.disabled_resource_packs_layout = UIScrollView(vertical=True, size_hint=(1, 1))

        open_resource_packs_folder_button = self.resource_manager.create_widget("open_resource_packs_folder_button")
        open_resource_packs_folder_button.set_callback(self._on_open_resource_packs_folder_button_clicked_)

        back_button = self.resource_manager.create_widget("resource_packs_back_button")
        back_button.set_callback(self._on_back_button_clicked_)

        update_packs_list_button = self.resource_manager.create_widget("update_packs_list_button")
        update_packs_list_button.set_callback(self._on_update_packs_list_button_clicked_)

        buttons_horizontal_layout = UIBoxLayout(vertical=False, align="bottom", size_hint=(1, 0.2), space_between=5)
        buttons_horizontal_layout.add(back_button)
        buttons_horizontal_layout.add(update_packs_list_button)

        resource_packs_scrolls_views_layout.add(self.disabled_resource_packs_layout)
        resource_packs_scrolls_views_layout.add(self.enabled_resource_packs_layout)
        base_vertical_layout.add(resource_packs_scrolls_views_layout)
        base_vertical_layout.add(open_resource_packs_folder_button)
        base_vertical_layout.add(buttons_horizontal_layout)

        anchor = UIAnchorLayout()
        anchor.add(background)
        anchor.add(menu_background, anchor_x="center_x", anchor_y="center_y")
        anchor.add(base_vertical_layout, anchor_x="center_x", anchor_y="center_y")
        self.update_resource_packs()
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


r = lambda: random.randint(0, 255)
print(f"{r()}, {r()}, {r()}")
