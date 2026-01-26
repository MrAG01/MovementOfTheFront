import arcade.color
from arcade.gui import UIAnchorLayout, UILabel, UIBoxLayout, UITextureButton, UIGridLayout, UIFlatButton

from GUI.ui_color_rect import UIColorRect
from GUI.ui_cost_layout_generator import generate_cost_layout, regenerate_cost_layout
from GUI.ui_scroll_view import UIScrollView
from GUI.ui_title_setter_layout import UITitleSetterLayout
from components.items import Items
from game.building.building_config import BuildingConfig
from game.building.client_building import ClientBuilding
from game.building.production.production_rule import ProductionRule
from game.unit.unit_config import UnitConfig
from resources.mods.mods_manager.mods_manager import ModsManager
from resources.resource_packs.resource_manager.resource_manager import ResourceManager


class UIProductionButton(UIAnchorLayout):
    def __init__(self, resource_manager: ResourceManager, _input: Items, _output: Items, callback, **kwargs):
        super().__init__(**kwargs)

        marging_layout = UIAnchorLayout(size_hint=(0.95, 0.9))

        self.activate_background = UIColorRect(color=arcade.color.Color(0, 0, 0, 0), size_hint=(1, 1))

        input_cost_layout = generate_cost_layout(resource_manager,
                                                 _input,
                                                 {"size_hint": (0.7, 0.5)}, local_base_width=50,
                                                 local_base_height=40, texture_size=30,
                                                 text_color=arcade.color.Color(196, 0, 0))
        font = resource_manager.get_default_font()
        input_layout = UITitleSetterLayout(UILabel(resource_manager.get_located_text("production_input", "text"),
                                                   font_size=16, font_name=font),
                                           input_cost_layout, size_hint=(1, 0.5), vertical=False)

        output_cost_layout = generate_cost_layout(resource_manager,
                                                  _output,
                                                  {"size_hint": (0.7, 0.5)}, local_base_width=50,
                                                  local_base_height=40, texture_size=30,
                                                  text_color=arcade.color.Color(0, 196, 0))

        output_layout = UITitleSetterLayout(UILabel(resource_manager.get_located_text("production_output", "text"),
                                                    font_size=16, font_name=font),
                                            output_cost_layout, size_hint=(1, 0.5), vertical=False)

        self.button: UIFlatButton = resource_manager.create_widget("production_button")
        self.button.on_click = callback

        marging_layout.add(input_layout, anchor_x="left", anchor_y="top")
        marging_layout.add(output_layout, anchor_x="left", anchor_y="bottom")

        self.add(self.button)
        self.add(self.activate_background)
        self.add(marging_layout)

    def set_hovered(self, hover):
        if hover:
            self.activate_background.color = arcade.color.Color(0, 200, 0, 50)
        else:
            self.activate_background.color = arcade.color.Color(0, 0, 0, 0)


class UIBuildingProductionMenu(UIAnchorLayout):
    def __init__(self, resource_manager, building, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.resource_manager: ResourceManager = resource_manager
        self.building = building
        self.callback = callback
        self.background = resource_manager.create_widget("secondary_background")

        self.add(self.background)
        self.buttons_list = {}
        self.current_activated_index = None

        self.main_scroll_area = UIScrollView(size_hint=(0.95, 0.9))
        self.add(self.main_scroll_area)

    def get_building(self):
        return self.building

    def _on_production_button_pressed(self, index):
        if self.callback and self.building:
            self.set_activated_production(index)
            self.callback(self.building.id, index)

    def set_callback(self, callback):
        self.callback = callback

    def set_building(self, building):
        self.building: ClientBuilding = building
        self.main_scroll_area.clear()
        self.current_activated_index = None
        if building is None:
            return
        if self.building.config.production is None:
            return
        self.buttons_list.clear()
        for i, rule in enumerate(self.building.config.production):
            rule: ProductionRule
            _input = rule.input
            _output = rule.output
            callback = lambda _, index=i: self._on_production_button_pressed(index)
            button = UIProductionButton(self.resource_manager, _input, _output, callback,
                                        size_hint=(1, None), height=80)

            self.main_scroll_area.add(button)
            self.buttons_list[i] = button
        index = self.building.production_index
        self.set_activated_production(index)

    def set_activated_production(self, index):
        if index != self.current_activated_index:
            if self.current_activated_index is not None:
                self.buttons_list[self.current_activated_index].set_hovered(False)
            self.current_activated_index = index
            self.buttons_list[index].set_hovered(True)


class UIBuildingBaseMenu(UIAnchorLayout):
    def __init__(self, resource_manager, building, **kwargs):
        super().__init__(**kwargs)
        self.resource_manager: ResourceManager = resource_manager
        self.background = resource_manager.create_widget("secondary_background")
        self.add(self.background)

        self.content_layout = UIBoxLayout(vertical=True, size_hint=(0.95, 0.95), space_between=10)
        font = resource_manager.get_default_font()
        self.name_label = UILabel("", font_size=28, size_hint=(1, 0.2), font_name=font)
        self.description_label = UILabel("", font_size=16, multiline=True, size_hint=(1, 0.4), font_name=font)

        self.delete_button = resource_manager.create_widget("building_base_menu_delete_button")

        self.update_button = resource_manager.create_widget("building_base_menu_update_button")

        self.bottom_buttons_layout = UIBoxLayout(vertical=False, size_hint=(1, 0.15), space_between=10)
        self.bottom_buttons_layout.add(self.delete_button)
        self.bottom_buttons_layout.add(self.update_button)

        self.content_layout.add(self.name_label)
        self.content_layout.add(self.description_label)

        # region CONSUMPTION
        consumption_anchor = UIAnchorLayout(size_hint=(1, 0.2))
        background = UIColorRect(color=arcade.color.Color(80, 80, 80), size_hint=(1, 1))

        main_layout = UIBoxLayout(vertical=True, size_hint=(1, 1))
        text = resource_manager.get_located_text("consumption_text", "text")
        self.consumption_label = UILabel(text, font_size=24, size_hint=(1, 0.5), font_name=font)
        main_layout.add(self.consumption_label)
        self.consumption_layout = generate_cost_layout(resource_manager, None, dict(size_hint=(1, 0.4)))
        main_layout.add(self.consumption_layout)

        consumption_anchor.add(background)
        consumption_anchor.add(main_layout)

        self.content_layout.add(consumption_anchor)
        # endregion

        self.content_layout.add(self.bottom_buttons_layout)

        self.add(self.content_layout)
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
        self.consumption_layout.clear()
        if self.building.config.consumption:
            regenerate_cost_layout(self.resource_manager, self.consumption_layout,
                                   self.building.config.consumption.production)
        self.name_label.text = name
        self.description_label.text = description


class UIUnitInfo(UIAnchorLayout):
    def __init__(self, resource_manager: ResourceManager, unit_config: UnitConfig, callback, **kwargs):
        super().__init__(**kwargs)

        marging_layout = UIAnchorLayout(size_hint=(0.95, 0.9))

        cost = unit_config.cost

        located_data = resource_manager.get_located_text(unit_config.name, "units")

        marging_layout.add(UILabel(text=located_data["name"], font_size=20, size_hint=(1, 0.2)),
                           anchor_x="left", anchor_y="top")
        marging_layout.add(
            UILabel(text=located_data["description"], font_size=14, size_hint=(1, 0.6), multiline=True),
            anchor_x="left", align_y=-5)

        self.cost_layout = generate_cost_layout(resource_manager,
                                                cost,
                                                {"size_hint": (0.5, 0.2)}, local_base_width=50,
                                                local_base_height=40, texture_size=30
                                                )

        texture = UITextureButton(texture=resource_manager.get_texture(unit_config.name).get(), width=60,
                                  height=60)
        marging_layout.add(texture, anchor_x="right", anchor_y="center")

        button = resource_manager.create_widget("add_unit_in_queue_button")
        button.on_click = lambda _: callback(unit_config)

        marging_layout.add(self.cost_layout, anchor_x="left", anchor_y="bottom")

        self.add(button)
        self.add(marging_layout)


class UIBuildingUnitsMenu(UIAnchorLayout):
    def __init__(self, resource_manager, mods_manager, building, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.resource_manager = resource_manager
        self.mods_manager = mods_manager
        self.building = building
        self.background = resource_manager.create_widget("secondary_background")

        self.units_grid_layout = UIGridLayout(size_hint=(1, 0.4), column_count=8, row_count=3)

        self.content_area = UIBoxLayout(vertical=True, size_hint=(0.96, 0.96))

        self.bottom_buttons_layout = UIBoxLayout(vertical=False, size_hint=(1, 0.6))

        self.content_area.add(self.units_grid_layout)
        self.content_area.add(self.bottom_buttons_layout)

        self.current_tablet_index = 0
        self.info_tablets_widgets = []

        self.content_anchor = UIScrollView(size_hint=(1, 1))

        self.bottom_buttons_layout.add(self.content_anchor)

        self.add(self.background)
        self.add(self.content_area)

        self.callback = callback

    def set_callback(self, callback):
        self.callback = callback

    def _on_add_in_queue_pressed(self, unit_config):
        if self.callback:
            self.callback(self.building.id, unit_config.name)

    def _on_unit_queue_changed(self):
        self.units_grid_layout.clear()
        w, h = self.units_grid_layout.size

        self.units_grid_layout.column_count = int(w // 64)
        self.units_grid_layout.row_count = 2

        cols = self.units_grid_layout.column_count
        rows = self.units_grid_layout.row_count

        for i, (unit_name, unit_data) in enumerate(self.building.units_queue):
            if i >= cols * rows:
                break

            texture = self.resource_manager.get_texture(unit_name)
            if not texture:
                continue

            row = i // cols
            column = i % cols

            button = UITextureButton(
                texture=texture.get(),
                width=64,
                height=64
            )
            self.units_grid_layout.add(
                child=button,
                column=column,
                row=row,
                column_span=1,
                row_span=1
            )

    def set_building(self, building):
        self.units_grid_layout.clear()
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
                                    size_hint=(1, None), height=90)
                self.content_anchor.add(widget)
                self.info_tablets_widgets.append(widget)
                # widget.visible = False
        if self.info_tablets_widgets:
            self.info_tablets_widgets[self.current_tablet_index].visible = True
        self._on_unit_queue_changed()
        self.building.set_on_unit_queue_changed_callback(self._on_unit_queue_changed)


class UIBuildingMenuTablet(UIAnchorLayout):
    def __init__(self, resource_manager: ResourceManager, mods_manager: ModsManager,
                 building: ClientBuilding = None,
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
        production_button.on_click = self._on_production_button_pressed

        self.upper_buttons_layout.add(base_button)
        self.upper_buttons_layout.add(production_button)
        self.upper_buttons_layout.add(units_button)

        self.widget_content_layout.add(self.upper_buttons_layout)

        anchor = UIAnchorLayout()

        self.building_base_menu = UIBuildingBaseMenu(self.resource_manager, building)
        anchor.add(self.building_base_menu)

        self.building_units_menu = UIBuildingUnitsMenu(self.resource_manager, mods_manager, building, None)
        anchor.add(self.building_units_menu)

        self.building_production_menu = UIBuildingProductionMenu(self.resource_manager, building)
        anchor.add(self.building_production_menu)

        self.widget_content_layout.add(anchor)

        self.add(self.widget_content_layout, anchor_x="center", anchor_y="center")
        self.visible = False
        self._on_base_button_pressed()

    def _on_base_button_pressed(self, *args):
        self.building_base_menu.visible = True
        self.building_units_menu.visible = False
        self.building_production_menu.visible = False

    def _on_units_button_pressed(self, *args):
        self.building_base_menu.visible = False
        self.building_units_menu.visible = True
        self.building_production_menu.visible = False

    def _on_production_button_pressed(self, *args):
        self.building_base_menu.visible = False
        self.building_units_menu.visible = False
        self.building_production_menu.visible = True

    def set_callbacks(self, on_delete_callback, on_update_callback, on_add_unit_in_queue_callback,
                      on_set_production_callback):
        self.building_base_menu.set_callbacks(on_delete_callback, on_update_callback)
        self.building_units_menu.set_callback(on_add_unit_in_queue_callback)
        self.building_production_menu.set_callback(on_set_production_callback)

    def set_building(self, building):
        # print(f"SETTING BUILDING: {building.id}")
        self.building = building

        self.building_base_menu.set_building(building)
        self.building_units_menu.set_building(building)
        self.building_production_menu.set_building(building)

        self.visible = self.building is not None
