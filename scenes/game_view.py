from threading import Lock
import arcade
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UILabel, UITextureButton, UIFlatButton
from arcade.gui.experimental.scroll_area import UIScrollBar
from arcade.gui import bind

from GUI.ui_building_info_tablet import UIBuildingMenuTablet
from GUI.ui_color_rect import UIColorRect
from GUI.ui_scroll_view import UIScrollView
from components.item import Item
from components.items import Items
from game.camera import Camera
from network.client.game_client import GameClient
from network.server.game_server import GameServer
from resources.mods.mods_manager.mods_manager import ModsManager
from resources.resource_packs.resource_manager.resource_manager import ResourceManager


class UIInventoryTablet(UIBoxLayout):
    def __init__(self, resource_manager, item: Item):
        super().__init__(vertical=False, size_hint=(1, 1))
        self.label = UILabel(text=str(item.amount), font_size=18, size_hint=(0.4, 1), text_color=(0, 0, 0, 255),
                             align="right")
        texture: arcade.Texture = resource_manager.get_texture(f"item_icon_{item.item_type}").get()
        self.texture_label = UITextureButton(texture=texture,
                                             width=texture.width,
                                             height=texture.height)

        self.add(self.label)
        self.add(self.texture_label)

    def update_value(self, new_item):
        self.label.text = str(new_item.amount)


class UIInventoryWidget(UIBoxLayout):
    def __init__(self, resource_manager, inventory: Items = None, **kwargs):
        super().__init__(vertical=False, space_between=20, **kwargs)
        self.resource_manager: ResourceManager = resource_manager
        self.items_widgets = {}
        if inventory is not None:
            for item_name, item in inventory:
                widget = UIInventoryTablet(self.resource_manager, item)
                self.items_widgets[item_name] = widget
                self.add(widget)

    def _update_values_impl(self, items):
        for item_name, item in items:
            if item_name in self.items_widgets:
                self.items_widgets[item_name].update_value(item)
            else:
                widget = UIInventoryTablet(self.resource_manager, item)
                self.items_widgets[item_name] = widget
                self.add(widget)

    def update_values(self, items: Items):
        if not arcade.get_window().has_exit:
            arcade.schedule_once(lambda dt: self._update_values_impl(items), 0)


class UIButtonWithIcon(UIAnchorLayout):
    def __init__(self, button, texture):
        super().__init__(size_hint=(1, None), height=50)
        self.add(button, anchor_y="center", anchor_x="center")
        self.add(texture, anchor_x="right", anchor_y="center")


class ButtonHoverObserver:
    def __init__(self, button, config, callback):
        self.hover_time = 0
        self.button = button
        self.callback = callback
        self.config = config
        self._original_on_update = getattr(button, 'on_update', None)

        def wrapped_on_update(*args, **kwargs):
            if self._original_on_update:
                self._original_on_update(*args, **kwargs)

            if self.button.hovered:
                self.hover_time += 1
                self.callback(self.config, self.hover_time)
            else:
                self.hover_time = 0

        self.button.on_update = wrapped_on_update


class UIBuildingsSelectorWidget(UIScrollView):
    def __init__(self, mods_manager, resource_manager, callback, hover_callback, **kwargs):
        super().__init__(vertical=True, scroll_speed=16, **kwargs)
        self.mods_manager: ModsManager = mods_manager
        self.resource_manager: ResourceManager = resource_manager
        self.callback = callback
        self.hover_callback = hover_callback

        self.observers = []

        for building_name, building_config in self.mods_manager.get_buildings().items():
            located_data = self.resource_manager.get_located_text(building_name, "buildings")
            button = self.resource_manager.create_widget("building_select_button")

            texture = UITextureButton(texture=self.resource_manager.get_texture(building_name).get(), width=40,
                                      height=40)
            icon_button = UIButtonWithIcon(button, texture)
            button.text = located_data["name"]
            button.on_click = lambda _, name=building_name: callback(name)
            self.observers.append(ButtonHoverObserver(button, building_config, hover_callback))
            self.add(icon_button)


class GameView(arcade.View):
    def __init__(self, client, view_setter, back_menu, resource_manager, mods_manager,
                 config_manager, keyboard_manager, mouse_manager, server=None):
        super().__init__()
        self.server: GameServer = server

        self.view_setter = view_setter
        self.back_menu = back_menu
        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager = mods_manager
        self.keyboard_manager = keyboard_manager
        self.main_camera = Camera(config_manager, keyboard_manager, mouse_manager)

        self.client: GameClient = client
        self.client.add_on_snapshot_listener(self.on_snapshot)
        self.client.add_on_game_disconnect_callback(self.on_disconnect)

        self.ui_manager_pause = UIManager()
        self.ui_manager_game = UIManager()

        self.pause = False
        self._setup_key_binds()

    def _setup_key_binds(self):
        self.keyboard_manager.register_callback("pause",
                                                on_pressed_callback=self._on_pause_button_pressed_)

    def _on_pause_continue_button_clicked_(self, event):
        self.pause = False
        self.ui_manager_pause.disable()

    def _on_settings_button_clicked_(self, event):
        pass

    def _on_exit_button_clicked_(self, event):
        if self.client is not None:
            self.client.disconnect()
            self.client = None
        if self.server is not None:
            self.server.shutdown()
            self.server = None
        # ОБРАБОТКА ВЫХОДА В ДРУГОЕ ОКНО В self.on_disconnect (ВЫЗЫВАЕТСЯ АВТОМАТИЧЕСКИ)

    def setup_game_gui(self):
        self.ui_manager_game.clear()

        inventory_anchor = UIAnchorLayout()
        self.inventory_gui = UIInventoryWidget(self.resource_manager, size_hint=(0.5, 0.05))
        self.selector_gui = UIBuildingsSelectorWidget(self.mods_manager, self.resource_manager,
                                                      self.client.input_handler.try_build,
                                                      self.client.input_handler.on_select_button_hover,
                                                      size_hint=(0.25, 0.6),
                                                      space_between=10)

        self.building_tablet_gui = UIBuildingMenuTablet(self.resource_manager, self.mods_manager,
                                                        None, size_hint=(0.3, 0.6))
        self.client.input_handler.attach_building_tablet_gui(self.building_tablet_gui)

        inventory_anchor.add(self.inventory_gui, anchor_x="center", anchor_y="top")
        inventory_anchor.add(self.selector_gui, anchor_x="left", anchor_y="center")
        inventory_anchor.add(self.building_tablet_gui, anchor_x="right", anchor_y="bottom", )
        # align_x=-10, align_y=10)
        self.ui_manager_game.add(inventory_anchor)
        self.ui_manager_game.enable()

    def setup_pause_gui(self):
        self.ui_manager_pause.clear()

        background_widget = UIColorRect(color=[0, 0, 0, 100], size_hint=(1, 1))
        layout = UIBoxLayout(vertical=True, size_hint=(0.4, 0.5), space_between=10)

        pause_continue_button = self.resource_manager.create_widget("pause_continue_button")
        pause_continue_button.on_click = self._on_pause_continue_button_clicked_

        settings_button = self.resource_manager.create_widget("settings_button")
        settings_button.on_click = self._on_settings_button_clicked_

        exit_button = self.resource_manager.create_widget("exit_button")
        exit_button.on_click = self._on_exit_button_clicked_

        layout.add(pause_continue_button)
        layout.add(settings_button)
        layout.add(exit_button)

        anchor = UIAnchorLayout()
        anchor.add(background_widget, anchor_x="center", anchor_y="center")
        anchor.add(layout, anchor_x="center", anchor_y="center")

        self.thread_lock = Lock()

        self.ui_manager_pause.add(anchor)

    def on_show_view(self) -> None:
        self.setup_pause_gui()
        self.setup_game_gui()

    def _on_pause_button_pressed_(self):
        if self.pause:
            self.ui_manager_pause.disable()
            self.pause = False
        else:
            self.ui_manager_pause.enable()
            self.pause = True

    def on_hide_view(self):
        self.ui_manager_pause.disable()
        self.client.disconnect()

    def on_draw(self):
        self.clear()
        self.main_camera.use()

        if self.client.game_state:
            width, height = self.client.game_state.map.get_size()
            self.main_camera.define_borders(width, height)
        self.client.draw(self.main_camera)

        self.ui_manager_game.draw()

        if self.pause:
            self.ui_manager_pause.draw()

    def on_snapshot(self, client):
        self_player = client.get_self_player()
        if self_player:
            self.inventory_gui.update_values(self_player.inventory.get_items())

    def on_disconnect(self):
        self.view_setter(self.back_menu)

    def on_update(self, delta_time):
        self.ui_manager_pause.on_update(delta_time)
        self.ui_manager_game.on_update(delta_time)
        if not self.pause:
            self.main_camera.update(delta_time)
        else:
            self.main_camera.delta_time = 0
        self.client.update(delta_time, self.pause)
