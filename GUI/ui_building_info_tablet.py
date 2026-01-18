from arcade.gui import UIAnchorLayout, UILabel, UIBoxLayout, UITextureButton, UIGridLayout
from game.building.building_config import BuildingConfig
from game.building.client_building import ClientBuilding
from game.unit.unit_config import UnitConfig
from resources.mods.mods_manager.mods_manager import ModsManager
from resources.resource_packs.resource_manager.resource_manager import ResourceManager


class UIBuildingBaseMenu(UIAnchorLayout):
    def __init__(self, resource_manager, building, **kwargs):
        super().__init__(**kwargs)
        self.resource_manager: ResourceManager = resource_manager
        self.background = resource_manager.create_widget("secondary_background")
        self.add(self.background)

        self.content_layout = UIBoxLayout(vertical=True, size_hint=(1, 1))

        self.name_label = UILabel("", font_size=28, size_hint=(1, 0.2), font_name="GNF")
        self.description_label = UILabel("", font_size=14, multiline=True, size_hint=(1, 0.6), font_name="GNF")

        self.delete_button = resource_manager.create_widget("building_base_menu_delete_button")

        self.update_button = resource_manager.create_widget("building_base_menu_update_button")

        self.bottom_buttons_layout = UIBoxLayout(vertical=False, size_hint=(1, 0.15), space_between=10)
        self.bottom_buttons_layout.add(self.delete_button)
        self.bottom_buttons_layout.add(self.update_button)

        self.content_layout.add(self.name_label)
        self.content_layout.add(self.description_label)
        self.content_layout.add(self.bottom_buttons_layout)

        self.add(self.content_layout, anchor_x="center", anchor_y="center")
        self.set_building(building)

    def set_callbacks(self, on_delete_button_pressed_callback, on_update_button_pressed_callback):
        self.delete_button.on_click = lambda _: on_delete_button_pressed_callback(self)
        self.update_button.on_click = lambda _: on_update_button_pressed_callback(self)

    def get_building(self):
        return self.building

    def set_building(self, building):
        self.building: ClientBuilding = building
        if building is None:
            return

        config: BuildingConfig = self.building.config
        located_data = self.resource_manager.get_located_text(config.name, "buildings")
        name = located_data["name"]
        description = located_data["description"]

        self.name_label.text = name
        self.description_label.text = description


class UIUnitInfo(UIAnchorLayout):
    def __init__(self, resource_manager: ResourceManager, unit_config: UnitConfig, callback, **kwargs):
        super().__init__(**kwargs)
        self.background = resource_manager.create_widget("secondary_background")
        self.content_layout = UIBoxLayout(vertical=True, size_hint=(1, 1))
        cost = unit_config.cost

        located_data = resource_manager.get_located_text(unit_config.name, "units")

        self.content_layout.add(UILabel(text=located_data["name"], font_size=16, size_hint=(1, 1)))
        self.content_layout.add(
            UILabel(text=located_data["description"], font_size=12, size_hint=(1, 1), multiline=True))

        for item_type, item_data in cost:
            icon_texture = resource_manager.get_texture(f"item_icon_{item_type}")
            amount = item_data.amount
            layout = UIBoxLayout(vertical=False, size_hint=(1, 1), space_between=10)

            icon_label = UITextureButton(texture=icon_texture.get(), width=32, height=32)
            label = UILabel(text=str(amount), font_size=16, size_hint=(1, 1))

            layout.add(icon_label)
            layout.add(label)

            self.content_layout.add(layout)
        button = resource_manager.create_widget("add_unit_in_queue_button")
        button.on_click = lambda _: callback(unit_config)
        self.content_layout.add(button)

        self.add(self.background)
        self.add(self.content_layout)


class UIBuildingUnitsMenu(UIAnchorLayout):
    def __init__(self, resource_manager, mods_manager, building, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.resource_manager = resource_manager
        self.mods_manager = mods_manager
        self.building = building
        self.background = resource_manager.create_widget("secondary_background")

        self.units_grid_layout = UIGridLayout(size_hint=(1, 0.3), column_count=8, row_count=3)

        self.content_area = UIBoxLayout(vertical=True, size_hint=(1, 1))

        self.bottom_buttons_layout = UIBoxLayout(vertical=False, size_hint=(1, 0.7))

        self.content_area.add(self.units_grid_layout)
        self.content_area.add(self.bottom_buttons_layout)

        self.current_tablet_index = 0
        self.info_tablets_widgets = []

        left_button = resource_manager.create_widget("building_info_unit_left_button")
        left_button.on_click = self._on_left_button_pressed
        self.content_anchor = UIAnchorLayout()

        right_button = resource_manager.create_widget("building_info_unit_right_button")
        right_button.on_click = self._on_right_button_pressed

        self.bottom_buttons_layout.add(left_button)
        self.bottom_buttons_layout.add(self.content_anchor)
        self.bottom_buttons_layout.add(right_button)

        self.add(self.background)
        self.add(self.content_area)

        self.callback = callback

    def set_callback(self, callback):
        self.callback = callback

    def _on_add_in_queue_pressed(self, unit_config):
        if self.callback:
            self.callback(self.building.id, unit_config.name)

    def _on_left_button_pressed(self, event):
        if not self.info_tablets_widgets:
            return
        self.info_tablets_widgets[self.current_tablet_index].visible = False
        self.current_tablet_index -= 1
        if self.current_tablet_index < 0:
            self.current_tablet_index = len(self.info_tablets_widgets) - 1
        self.info_tablets_widgets[self.current_tablet_index].visible = True

    def _on_right_button_pressed(self, event):
        if not self.info_tablets_widgets:
            return
        self.info_tablets_widgets[self.current_tablet_index].visible = False
        self.current_tablet_index += 1
        self.current_tablet_index %= len(self.info_tablets_widgets)
        self.info_tablets_widgets[self.current_tablet_index].visible = True

    def _on_unit_queue_changed(self):
        self.units_grid_layout.clear()

        rows_number = self.units_grid_layout.row_count
        cols_number = self.units_grid_layout.column_count

        for i, (unit_name, t) in enumerate(self.building.units_queue):
            texture = self.resource_manager.get_texture(unit_name)

            row = i // cols_number
            col = i % cols_number

            self.units_grid_layout.add(UITextureButton(texture=texture.get(), width=32, height=32,
                                                       row=row, col=col))

    def set_building(self, building):
        self.content_anchor.clear()
        self.info_tablets_widgets.clear()
        self.current_tablet_index = 0
        if self.building:
            self.building.reset_on_unit_queue_changed_callback()
        self.building: ClientBuilding = building
        if building is None:
            return
        config: BuildingConfig = self.building.config
        can_spawn_units = config.can_spawn_units
        if can_spawn_units:
            for unit_type in can_spawn_units:
                unit_config = self.mods_manager.get_unit(unit_type)
                widget = UIUnitInfo(self.resource_manager, unit_config, self._on_add_in_queue_pressed,
                                    size_hint=(0.95, None))
                self.content_anchor.add(widget)
                self.info_tablets_widgets.append(widget)
                widget.visible = False
        if self.info_tablets_widgets:
            self.info_tablets_widgets[self.current_tablet_index].visible = True
        self.building.set_on_unit_queue_changed_callback(self._on_unit_queue_changed)


class UIBuildingMenuTablet(UIAnchorLayout):
    def __init__(self, resource_manager: ResourceManager, mods_manager: ModsManager, building: ClientBuilding = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.resource_manager = resource_manager
        self.mods_manager = mods_manager
        self.building = building

        self.main_background = self.resource_manager.create_widget("main_menu_background")
        self.add(self.main_background, anchor_x="center", anchor_y="center")

        self.widget_content_layout = UIBoxLayout(vertical=True, size_hint=(0.95, 0.95), space_between=5)
        self.upper_buttons_layout = UIBoxLayout(vertical=False, size_hint=(1, 0.12), space_between=5)

        base_button = self.resource_manager.create_widget("building_menu_base_button")
        production_button = self.resource_manager.create_widget("building_menu_production_button")
        units_button = self.resource_manager.create_widget("building_menu_units_button")

        base_button.on_click = self._on_base_button_pressed
        units_button.on_click = self._on_units_button_pressed

        self.upper_buttons_layout.add(base_button)
        self.upper_buttons_layout.add(production_button)
        self.upper_buttons_layout.add(units_button)

        self.widget_content_layout.add(self.upper_buttons_layout)

        anchor = UIAnchorLayout()

        self.building_base_menu = UIBuildingBaseMenu(self.resource_manager, building)
        self.building_base_menu.visible = False
        anchor.add(self.building_base_menu)

        self.building_units_menu = UIBuildingUnitsMenu(self.resource_manager, mods_manager, building, None)
        anchor.add(self.building_units_menu)

        self.widget_content_layout.add(anchor)

        self.add(self.widget_content_layout, anchor_x="center", anchor_y="center")
        self.visible = False

    def _on_base_button_pressed(self, *args):
        self.building_base_menu.visible = True
        self.building_units_menu.visible = False

    def _on_units_button_pressed(self, *args):
        self.building_base_menu.visible = False
        self.building_units_menu.visible = True

    def set_callbacks(self, on_delete_callback, on_update_callback, on_add_unit_in_queue_callback):
        self.building_base_menu.set_callbacks(on_delete_callback, on_update_callback)
        self.building_units_menu.set_callback(on_add_unit_in_queue_callback)

    def set_building(self, building):
        self.building = building

        self.building_base_menu.set_building(building)
        self.building_units_menu.set_building(building)

        self.visible = self.building is not None
