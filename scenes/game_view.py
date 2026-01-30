import time
from threading import Lock
import arcade
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UILabel, UITextureButton, Surface, UIEvent, \
    UIMouseDragEvent, UIMouseScrollEvent
from arcade.gui.ui_manager import W
from pyglet.event import EVENT_UNHANDLED

from GUI.ui_building_info_tablet import UIBuildingMenuTablet
from GUI.ui_color_rect import UIColorRect
from GUI.ui_scroll_view import UIScrollView
from GUI.ui_texture import UITexture
from GUI.ui_title_setter_layout import UITitleSetterLayout
from components.item import Item
from components.items import Items
from game.camera import Camera
from network.client.game_client import GameClient
from network.server.game_server import GameServer
from resources.mods.mods_manager.mods_manager import ModsManager
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from utils.function_observer import function_observer
from utils.time_counter import time_counter


class UIInventoryTablet(UIBoxLayout):
    def __init__(self, resource_manager, item: Item):
        super().__init__(vertical=False, size_hint=(1, 1))
        self.label = UILabel(text=str(item.amount), font_size=20, size_hint=(0.4, 1), text_color=(255, 255, 255, 255),
                             font_name=resource_manager.get_default_font(),
                             align="right")
        texture: arcade.Texture = resource_manager.get_texture(f"item_icon_{item.item_type}").get()
        self.texture_label = UITexture(texture=texture,
                                       width=texture.width,
                                       height=texture.height)

        self.add(self.label)
        self.add(self.texture_label)

    def update_value(self, new_item):
        self.label.text = str(new_item.amount)


class UIInventoryWidget(UIAnchorLayout):
    def __init__(self, resource_manager: ResourceManager, inventory: Items = None, **kwargs):
        super().__init__(**kwargs)
        background = resource_manager.create_widget("menus_background", size_hint=(1, 1))
        self.main_layout = UIBoxLayout(size_hint=(1, 1), vertical=False, space_between=20)
        self.resource_manager: ResourceManager = resource_manager
        self.items_widgets = {}

        if inventory is not None:
            for item_name, item in inventory:
                widget = UIInventoryTablet(self.resource_manager, item)
                self.items_widgets[item_name] = widget
                self.main_layout.add(widget)

        self.add(background, anchor_x="center", anchor_y="center")
        self.add(self.main_layout, anchor_x="center", anchor_y="center")

    def _update_values_impl(self, items):
        for item_name, item in items:
            if item_name in self.items_widgets:
                self.items_widgets[item_name].update_value(item)
            else:
                widget = UIInventoryTablet(self.resource_manager, item)
                self.items_widgets[item_name] = widget
                self.main_layout.add(widget)

    def update_values(self, items: Items):
        if not arcade.get_window().has_exit:
            arcade.schedule_once(lambda dt: self._update_values_impl(items), 0)


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


class UIBuildingButton(UIAnchorLayout):
    ITEMS_POWER = {
        "peoples": 1,
        "food": 1,
        "wood": 2,
        "stone": 3,
        "planks": 10,
        "iron": 12,
        "tools": 25,
        "wheat": 4,
        "iron_ore": 5,
        "gold_ore": 15,
        "gold": 40,
        "concrete": 30,
        "steel": 50,
        "parts": 60,
        "coal": 20,
    }

    def __init__(self, resource_manager, text, callback, texture, cost):
        super().__init__(size_hint=(1, None), height=50)

        marging_layout = UIAnchorLayout(size_hint=(0.95, 0.9))
        self.raw_button = resource_manager.create_widget("building_select_button")
        self.raw_button.text = ""
        self.raw_button.set_callback(callback)
        self.raw_button.visible = False
        self.raw_button.disabled = True

        # self.raw_button_disabled = resource_manager.create_widget("building_select_button_disabled")
        # self.raw_button_disabled.text = ""
        font = resource_manager.get_default_font()
        self.text_label = UILabel(text, font_name=font, font_size=18, multiline=True, size_hint=(0.8, None))

        self.add(self.raw_button, anchor_x="center", anchor_y="center")
        # self.add(self.raw_button_disabled)

        marging_layout.add(self.text_label, anchor_x="left", anchor_y="top")
        marging_layout.add(texture, anchor_x="right", anchor_y="center")
        self.cost: Items = cost
        self.cost_layout = UIBoxLayout(vertical=False, size_hint=(0.5, 0.2))
        if cost:
            for item_name, item in cost:
                local_layout = UIBoxLayout(vertical=False, width=30, height=10, space_between=2)
                # print(f"item_icon_{item_name}")
                raw_texture = resource_manager.get_texture(f"item_icon_{item_name}")
                item_texture = UITexture(texture=raw_texture.get(), width=20,
                                         height=20)
                local_layout.add(item_texture)
                local_layout.add(UILabel(str(item.amount), font_name=font, font_size=10))

                self.cost_layout.add(local_layout)
        else:
            self.cost_layout.add(
                UILabel(resource_manager.get_located_text("free_text", "text"), font_name=font, font_size=12))
        marging_layout.add(self.cost_layout, anchor_x="left", anchor_y="bottom")
        self.add(marging_layout)

        self.baked_layout = False

    @staticmethod
    def get_item_power(item_name):
        return UIBuildingButton.ITEMS_POWER[item_name]

    def get_total_getting_difficulty(self):
        items_number = len(self.cost.items)
        total_amount = sum(
            [item.amount * UIBuildingButton.get_item_power(item.item_type) for item in self.cost.items.values()])
        return items_number, total_amount

    def update_state(self, inventory: Items):
        enabled = inventory.has_amount(self.cost)

        if hasattr(self, "prev_state"):
            if self.prev_state == enabled:
                return
        self.prev_state = enabled

        self.raw_button.disabled = not enabled

        if enabled:
            self.raw_button.visible = True
            self.text_label.update_font(font_color=arcade.color.Color(255, 255, 255))
        else:
            self.raw_button.visible = False
            self.text_label.update_font(font_color=arcade.color.Color(100, 100, 100))


class UIBuildingsSelectorWidget(UIScrollView):
    def __init__(self, mods_manager, resource_manager, callback, hover_callback, **kwargs):
        super().__init__(vertical=True, scroll_speed=16, background_color=arcade.color.Color(10, 10, 10), **kwargs)
        self.mods_manager: ModsManager = mods_manager
        self.resource_manager: ResourceManager = resource_manager
        self.callback = callback
        self.hover_callback = hover_callback

        self.buttons = set()

        for building_name, building_config in self.mods_manager.get_buildings().items():
            if not building_config.can_build:
                continue
            located_data = self.resource_manager.get_located_text(building_name, "buildings")
            texture = UITexture(texture=self.resource_manager.get_texture(building_name).get(), width=40,
                                height=40)
            text = located_data["name"] if located_data else ""
            icon_button = UIBuildingButton(self.resource_manager, text,
                                           lambda _, name=building_name: callback(name),
                                           texture, building_config.cost)
            self.buttons.add(icon_button)
            self.add(icon_button)
        self.content_layout._children.sort(key=lambda el: el.child.get_total_getting_difficulty())
        self.baked = False
        self.baked_layout = False
        self.baked_surface = None

    def update_state(self, inventory):
        for button in self.buttons:
            button.update_state(inventory)


class OptimizedUIManager(UIManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layouts_baked_timer = 0

    def execute_layout(self, force=False):
        if self.layouts_baked_timer < 10 or force:
            super().execute_layout()
            self.layouts_baked_timer += 1


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
        self.client.attach_game_view(self)

        self.client.attach_camera(self.main_camera)
        self.client.add_on_snapshot_listener(self.on_snapshot)
        self.client.add_on_game_disconnect_callback(self.on_disconnect)

        self.ui_manager_pause = UIManager()
        self.ui_manager_game = UIManager()
        self.selector_gui_game_manager = OptimizedUIManager()
        self.building_tablet_ui_manager = OptimizedUIManager()
        self.debug_mode = True
        self.pause = False

        self.game_over_ui_manager = UIManager()
        self.game_ended = False

        self._setup_key_binds()

    def setup_game_over_ui(self, data):
        self.game_over_ui_manager.enable()
        anchor = UIAnchorLayout()

        background_widget = UIColorRect(color=[0, 0, 0, 100], size_hint=(1, 1))
        layout = UIBoxLayout(vertical=True, size_hint=(0.7, 0.2))

        client_names = self.client.get_clients_list()
        winner_id = data["winner"]
        winner_client_name = ""
        for (name, client_id), ping in client_names:
            if winner_id == client_id:
                winner_client_name = name
                break

        text_label = self.resource_manager.create_widget("winner_label")
        # print(winner_client_name, client_names, winner_id)
        text_label.text = winner_client_name
        layout.add(UITitleSetterLayout(self.resource_manager.create_widget("winner_helper_label"),
                                       text_label, vertical=False, size_hint=(1, 1)))

        # buttons_layout = UIBoxLayout(vertical=False, size_hint=(1, 0.1))
        back_button = self.resource_manager.create_widget("back_button")
        back_button.set_callback(self.on_back_button)
        # buttons_layout.add(back_button)

        layout.add(back_button)

        anchor.add(background_widget)
        anchor.add(layout)

        self.game_over_ui_manager.add(anchor)

    def on_back_button(self, event):
        self._on_exit_button_clicked_(event)
        self.on_disconnect()

    def init_winner_menu(self, data):
        def true_func(dt):
            self.setup_game_over_ui(data)
            self.ui_manager_game.disable()
            self.ui_manager_pause.disable()
            self.game_ended = True

        arcade.schedule_once(true_func, 0)

    def on_selector_visible_change_button_pressed(self):
        if hasattr(self, "selector_gui"):
            self.selector_gui.visible = not self.selector_gui.visible

    def _setup_key_binds(self):
        self.keyboard_manager.register_callback("pause",
                                                on_pressed_callback=self._on_pause_button_pressed_)
        self.keyboard_manager.register_callback("selector_visible_change",
                                                on_pressed_callback=self.on_selector_visible_change_button_pressed)

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

    def set_debug_mode(self, state):
        self.fps_label.visible = state
        self.debug_mode = state

    def setup_game_gui(self):
        self.ui_manager_game.clear()

        inventory_anchor = UIAnchorLayout()
        self.inventory_gui = UIInventoryWidget(self.resource_manager, size_hint=(0.8, 0.05))

        self.fps_label = UILabel("FPS: NONE", font_size=20, font_name=self.resource_manager.get_default_font(),
                                 size_hint=(0.15, 0.05))
        self.set_debug_mode(False)
        inventory_anchor.add(self.inventory_gui, anchor_x="center", anchor_y="top")
        inventory_anchor.add(self.fps_label, anchor_x="left", anchor_y="top")

        self.ui_manager_game.add(inventory_anchor)
        self.ui_manager_game.enable()

        self.selector_gui_game_manager.clear()

        self.selector_gui = UIBuildingsSelectorWidget(self.mods_manager, self.resource_manager,
                                                      self.client.input_handler.try_build,
                                                      self.client.input_handler.on_select_button_hover,
                                                      size_hint=(0.25, 0.6),
                                                      space_between=10)

        anchor = UIAnchorLayout()
        anchor.add(self.selector_gui, anchor_x="left", anchor_y="center")
        self.selector_gui_game_manager.add(anchor)
        self.selector_gui_game_manager.enable()

        self.building_tablet_ui_manager.clear()
        self.building_tablet_gui = UIBuildingMenuTablet(self.resource_manager, self.mods_manager,
                                                        self.building_tablet_ui_manager,
                                                        None, size_hint=(0.3, 0.6))
        self.building_tablet_gui.visible = False
        self.client.input_handler.attach_building_tablet_gui(self.building_tablet_gui)
        anchor = UIAnchorLayout()
        anchor.add(self.building_tablet_gui, anchor_x="right", anchor_y="bottom")
        self.building_tablet_ui_manager.add(anchor)
        self.building_tablet_ui_manager.enable()

    def setup_pause_gui(self):
        self.ui_manager_pause.clear()

        background_widget = UIColorRect(color=[0, 0, 0, 100], size_hint=(1, 1))
        layout = UIBoxLayout(vertical=True, size_hint=(0.4, 0.5), space_between=10)

        pause_continue_button = self.resource_manager.create_widget("pause_continue_button")
        pause_continue_button.set_callback(self._on_pause_continue_button_clicked_)

        settings_button = self.resource_manager.create_widget("settings_button")
        settings_button.set_callback(self._on_settings_button_clicked_)

        exit_button = self.resource_manager.create_widget("exit_button")
        exit_button.set_callback(self._on_exit_button_clicked_)

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

    # @time_counter
    def _draw_game_gui(self):
        self.ui_manager_game.draw()
        self.selector_gui_game_manager.draw()
        self.building_tablet_ui_manager.draw()

    def _draw_game(self):
        self.client.draw(self.main_camera)

    def _draw_pause(self):
        self.ui_manager_pause.draw()

    def on_draw(self):
        start_time = time.time()

        self.clear()
        self.main_camera.use()

        if self.client.game_state:
            width, height = self.client.game_state.map.get_size()
            self.main_camera.define_borders(width, height)
        self._draw_game()
        if not self.game_ended:
            self._draw_game_gui()

        if self.pause and not self.game_ended:
            self._draw_pause()
        # self.game_over_ui_manager.draw()

        end_time = time.time()
        ft = end_time - start_time
        if ft != 0:
            fps = 1 / ft
            self.fps_label.text = f"FPS: {fps:.1f}"
        # time.sleep(1 - ft)

    def on_snapshot(self, client):
        self_player = client.get_self_player()
        if self_player:
            inventory = self_player.inventory.get_items()
            if hasattr(self, "inventory_gui"):
                self.inventory_gui.update_values(inventory)
            if hasattr(self, "selector_gui"):
                self.selector_gui.update_state(inventory)

    def on_disconnect(self):
        arcade.schedule(lambda dt: self.view_setter(self.back_menu), 0)

    def on_update(self, delta_time):
        self.ui_manager_pause.on_update(delta_time)
        self.ui_manager_game.on_update(delta_time)
        self.game_over_ui_manager.on_update(delta_time)
        if not self.pause and not self.game_ended:
            self.main_camera.update(delta_time)
        else:
            self.main_camera.delta_time = 0
        self.client.update(delta_time, self.pause)
