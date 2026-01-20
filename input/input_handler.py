import math

from arcade.types import AnchorPoint

from GUI.ui_building_info_tablet import UIBuildingMenuTablet, UIBuildingBaseMenu
from game.building.building_config import BuildingConfig
from game.building.client_building import ClientBuilding
from game.camera import Camera
from game.deposits.client_deposit import ClientDeposit
from game.unit.client_unit import ClientUnit
from input.keyboard_manager import KeyboardManager
from input.mouse_manager import MouseManager
from network.client.request.client_requests import ClientRequest
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
import arcade
import pyglet


class InputHandler:
    def __init__(self, resource_manager, mods_manager, keyboard_manager, mouse_manager, tick_rate, send_callback,
                 client):
        self.pending_requests = []
        self.send_callback = send_callback
        self.client = client
        self.player = self.client.get_self_player()

        self.keyboard_manager: KeyboardManager = keyboard_manager
        self.mouse_manager: MouseManager = mouse_manager

        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager = mods_manager

        self.tick_time = 1 / tick_rate
        self.time_counter = 0
        self.camera = None
        self._setup_key_binds()

        self.selected_building_config: BuildingConfig = None
        self.selected_building_type = None
        self.selected_building_texture = None

        self.wanted_select_building_exist = None
        self.selected_building_exist = None

        self.building_tablet_gui: UIBuildingMenuTablet = None

        self.selection_rect = []

        self.selected_units = []

        self.units_path_length = 0
        self.units_path_drawing_parts = []

    def attach_building_tablet_gui(self, building_tablet_gui):
        self.building_tablet_gui = building_tablet_gui
        self.building_tablet_gui.set_callbacks(self._on_delete_building, self._on_update_building,
                                               self._on_add_unit_in_queue)

    def _on_add_unit_in_queue(self, building_id, unit_type):
        self.add_request(ClientRequest.create_unit_add_in_queue_request(building_id, unit_type))

    def _on_delete_building(self, menu: UIBuildingBaseMenu):
        building = menu.get_building()
        if building is None:
            return

        self.building_tablet_gui.set_building(None)
        self.add_request(ClientRequest.create_destroy_request(building.id))

    def _on_update_building(self, menu: UIBuildingBaseMenu):
        pass

    def _try_to_get_player(self):
        self.player = self.client.get_self_player()

    def attach_camera(self, camera):
        self.camera = camera

    def unselect_building_place(self):
        self.selected_building_config = None
        self.selected_building_type = None
        self.selected_building_texture = None

    def _on_escape_pressed(self):
        self.unselect_building_place()

    def _setup_key_binds(self):
        self.keyboard_manager.register_callback("unselect_building", on_pressed_callback=self._on_escape_pressed)
        self.mouse_manager.register_on_pressed_callback(self.on_mouse_pressed)

        self.mouse_manager.register_on_dragging_callback(self.on_mouse_drag)
        self.mouse_manager.register_on_released_callback(self.on_mouse_release)

    def on_select_button_hover(self, building_config, hovered):
        # if hovered > 100:
        #    self.try_to_open_ui_building_info_tablet(building_config)
        pass

    def try_build(self, building_name):
        if self.selected_building_type == building_name:
            self.unselect_building_place()
        else:
            self.selected_building_type = building_name
            self.selected_building_texture = self.resource_manager.get_texture(building_name)
            self.selected_building_config = self.mods_manager.get_building(building_name)

    def add_request(self, request):
        self.pending_requests.append(request)

    def update(self, delta_time):
        self.time_counter += delta_time
        if self.time_counter >= self.tick_time:
            self.time_counter = 0
            self.pending_requests.append(ClientRequest.create_ping_request())
            self.send_callback([request.serialize() for request in self.pending_requests])
            self.pending_requests.clear()
        if self.camera is None:
            return
        sx, sy = self.mouse_manager.get_mouse_pos()
        x, y, _ = self.camera.unproject(arcade.Vec2(sx, sy))

        closest_building = self._get_closest_buildings(x, y)

        if closest_building is not None:
            # print(closest_building.position)
            if self.wanted_select_building_exist is not None:
                if self.wanted_select_building_exist != closest_building:
                    self.wanted_select_building_exist.disable_outline()
                    self.wanted_select_building_exist = closest_building
                    self.wanted_select_building_exist.enable_outline()
            else:
                self.wanted_select_building_exist = closest_building
                self.wanted_select_building_exist.enable_outline()
        else:
            if self.wanted_select_building_exist is not None:
                self.wanted_select_building_exist.disable_outline()
            self.wanted_select_building_exist = None

    def _get_closest_deposit(self, x, y):
        zoom_sqr = self.camera.zoom ** 2

        if self.selected_building_config.can_place_on_deposit:
            deposits_close = self.client.game_state.map.get_deposits_close_to(x, y)
            closest_deposit = [(40 ** 2) / zoom_sqr, None]
            for deposit in deposits_close:
                deposit: ClientDeposit
                if deposit.has_owner():
                    continue
                dx, dy = deposit.position
                distance_sqr = ((x - dx) ** 2 + (y - dy) ** 2)
                if distance_sqr < closest_deposit[0]:
                    closest_deposit[0] = distance_sqr
                    closest_deposit[1] = deposit
            closest_deposit = closest_deposit[1]
            if closest_deposit is not None:
                return closest_deposit
        return None

    def _get_closest_unit(self, x, y):
        zoom_sqr = self.camera.zoom ** 2

        units_close = self.player.get_units_close_to(x, y)
        closest_unit = [(40 ** 2) / zoom_sqr, None]
        for unit in units_close:
            unit: ClientDeposit
            if unit.has_owner():
                continue
            dx, dy = unit.position
            distance_sqr = ((x - dx) ** 2 + (y - dy) ** 2)
            if distance_sqr < closest_unit[0]:
                closest_unit[0] = distance_sqr
                closest_unit[1] = unit
        closest_unit = closest_unit[1]
        if closest_unit is not None:
            return closest_unit

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT and modifiers & pyglet.window.key.MOD_SHIFT:
            if self.selection_rect:
                self.selection_rect[2] += dx
                self.selection_rect[3] += dy
            else:
                self.selection_rect = [x, y, x, y]
        elif buttons & pyglet.window.mouse.RIGHT:
            if self.selected_units:
                x, y, _ = self.camera.unproject(arcade.Vec2(x, y))
                if not self.units_path_drawing_parts:
                    self.units_path_drawing_parts.append((x, y))
                    self.units_path_length = 0
                else:
                    px, py = self.units_path_drawing_parts[-1]
                    distance_sqr = (px - x) ** 2 + (py - y) ** 2
                    if distance_sqr > 5 ** 2:
                        self.units_path_drawing_parts.append((x, y))
                        self.units_path_length += math.sqrt(distance_sqr)

    def _disable_units_selection(self):
        for unit in self.selected_units:
            unit.disable_selection()
        self.selected_units.clear()

    def _process_selection(self, rect):
        x1, y1, x2, y2 = rect

        x1, y1, _ = self.camera.unproject(arcade.Vec2(x1, y1))
        x2, y2, _ = self.camera.unproject(arcade.Vec2(x2, y2))

        # print([x1, y1, x2, y2], rect)
        self._disable_units_selection()
        self.selected_units = self.player.get_units_in_rect([x1, y1, x2, y2])
        # print()
        for unit in self.selected_units:
            unit: ClientUnit
            unit.enable_selection()

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT and self.selection_rect:
            self.selection_rect[2] = x
            self.selection_rect[3] = y
            self._process_selection(self.selection_rect)
            self.selection_rect.clear()
        elif button == pyglet.window.mouse.RIGHT:
            if self.selected_units and self.units_path_drawing_parts:
                self._process_massive_units_push(self.selected_units, self._get_units_walk_targets())
            self.units_path_drawing_parts.clear()
            self.units_path_length = 0

    def _process_massive_units_push(self, units, targets):
        not_used_units = set(units)
        for tx, ty in targets:
            closest_unit = None
            for unit in not_used_units:
                x, y = unit.position
                distance_sqr = (tx - x) ** 2 + (ty - y) ** 2
                if closest_unit is None:
                    closest_unit = [distance_sqr, unit]
                elif closest_unit[0] > distance_sqr:
                    closest_unit[0] = distance_sqr
                    closest_unit[1] = unit
            if closest_unit is not None:
                unit = closest_unit[1]
                not_used_units.remove(unit)
                self.add_request(ClientRequest.create_unit_new_path(unit.id, [[tx, ty]]))

    def on_mouse_pressed(self, x, y, button, modifiers):
        if self.camera is None:
            return

        if modifiers == arcade.key.MOD_SHIFT:
            if button == pyglet.window.mouse.LEFT:
                pass
            return

        if button == pyglet.window.mouse.RIGHT:
            if self.selected_building_type:
                self.unselect_building_place()
        if button != pyglet.window.mouse.LEFT:
            return
        if self.selected_units:
            self._disable_units_selection()
        if self.selected_building_type:
            x, y, _ = self.camera.unproject(arcade.Vec2(x, y))
            linked_deposit = self._get_closest_deposit(x, y)
            if linked_deposit:
                x, y = linked_deposit.position
                arg = linked_deposit.can_place_building_on(self.selected_building_type)
            else:
                arg = False
            biome = self.client.game_state.map.get_biome(x, y)

            can_build = biome.can_build_on and (
                    (self.selected_building_config.can_place_on_deposit and arg) or
                    self.selected_building_config.can_place_not_on_deposit)
            if can_build:
                self.add_request(ClientRequest.create_build_request(x, y, self.selected_building_type, linked_deposit))
        else:

            if self.wanted_select_building_exist is not None:
                if self.selected_building_exist == self.wanted_select_building_exist:
                    self.building_tablet_gui.set_building(building=None)
                    self.selected_building_exist.disable_selection()
                    self.selected_building_exist = None
                else:
                    if self.selected_building_exist is not None:
                        self.building_tablet_gui.set_building(building=None)
                        self.selected_building_exist.disable_selection()
                        self.selected_building_exist = None
                    self.selected_building_exist = self.wanted_select_building_exist
                    self.building_tablet_gui.set_building(building=self.selected_building_exist)
                    self.selected_building_exist.enable_selection()
            else:
                if self.selected_building_exist is not None:
                    self.building_tablet_gui.set_building(building=None)
                    self.selected_building_exist.disable_selection()
                    self.selected_building_exist = None

    def _get_closest_buildings(self, x, y):
        if self.player is None:
            self._try_to_get_player()
            return
        zoom_sqr = self.camera.zoom ** 2

        close_buildings = self.player.get_closest_buildings_to(x, y)
        closest_buildings = [50 ** 2 / zoom_sqr, None]
        for building in close_buildings:
            building: ClientBuilding

            dx, dy = building.position
            distance_sqr = (x - dx) ** 2 + (y - dy) ** 2
            if distance_sqr < closest_buildings[0]:
                closest_buildings[0] = distance_sqr
                closest_buildings[1] = building
        closest_building = closest_buildings[1]
        if closest_building is not None:
            return closest_building
        return None

    def _get_units_walk_targets(self):
        if not (self.selected_units and self.units_path_drawing_parts):
            return None

        if len(self.selected_units) == 1:
            return [self.units_path_drawing_parts[-1]]

        if self.units_path_length <= 0:
            return None

        density = self.units_path_length / (len(self.selected_units) - 1)

        total_distance = 0
        result = []

        for i in range(len(self.units_path_drawing_parts) - 1):
            start_point = self.units_path_drawing_parts[i]
            end_point = self.units_path_drawing_parts[i + 1]
            segment_length = math.hypot(end_point[0] - start_point[0], end_point[1] - start_point[1])

            if segment_length == 0:
                continue

            segment_direction = (
                (end_point[0] - start_point[0]) / segment_length,
                (end_point[1] - start_point[1]) / segment_length
            )

            segment_start_distance = total_distance
            segment_end_distance = total_distance + segment_length

            while len(result) < len(self.selected_units):
                target_distance = len(result) * density

                if target_distance > segment_end_distance:
                    break

                if segment_start_distance <= target_distance <= segment_end_distance:
                    distance_on_segment = target_distance - segment_start_distance
                    marker_x = start_point[0] + segment_direction[0] * distance_on_segment
                    marker_y = start_point[1] + segment_direction[1] * distance_on_segment
                    result.append((marker_x, marker_y))

            total_distance += segment_length

            if len(result) >= len(self.selected_units):
                break

        if result:
            result[0] = self.units_path_drawing_parts[0]
        else:
            result.append(self.units_path_drawing_parts[0])

        result = result[:len(self.selected_units)]
        if len(result) == len(self.selected_units):
            result[-1] = self.units_path_drawing_parts[-1]

        return result

    def draw(self, camera: Camera):
        if self.camera is None:
            self.attach_camera(camera)

        sx, sy = self.mouse_manager.get_mouse_pos()
        x, y, _ = camera.unproject(arcade.Vec2(sx, sy))

        if self.selected_building_texture:
            zoom_k = 1 / camera.zoom
            linked_deposit = self._get_closest_deposit(x, y)

            if linked_deposit:
                x, y = linked_deposit.position
                arg = linked_deposit.can_place_building_on(self.selected_building_type)
            else:
                arg = False
            biome = self.client.game_state.map.get_biome(x, y)

            can_build = biome.can_build_on and (
                    (self.selected_building_config.can_place_on_deposit and arg) or
                    self.selected_building_config.can_place_not_on_deposit)
            color = arcade.color.Color(0, 255, 0) if can_build else arcade.color.Color(255, 0, 0)
            self.selected_building_texture.draw(x, y, zoom_k, zoom_k, color=color)

        if self.selection_rect:
            x1, y1, x2, y2 = self.selection_rect

            w, h = (x2 - x1) / camera.zoom, (y2 - y1) / camera.zoom

            x, y, _ = camera.unproject(arcade.Vec2(x1, y1))
            arcade.draw_rect_outline(arcade.rect.XYWH(x - 1, y - 1, w + 2, h + 2, AnchorPoint.BOTTOM_LEFT),
                                     arcade.color.Color(120, 120, 20, 200), 2 / self.camera.zoom)
            arcade.draw_rect_filled(arcade.rect.XYWH(x, y, w, h, AnchorPoint.BOTTOM_LEFT),
                                    arcade.color.Color(100, 100, 20, 100))
        if self.units_path_drawing_parts and self.selected_units:
            x, y, _ = camera.unproject(arcade.Vec2(sx, sy))

            arcade.draw_line_strip(self.units_path_drawing_parts, arcade.color.Color(255, 255, 255),
                                   3 / self.camera.zoom)
            # arcade.draw_line(*self.units_path_drawing_parts[-1], x, y, arcade.color.Color(255, 255, 255),
            #                 3 / self.camera.zoom)

            units_targets_pos = self._get_units_walk_targets()
            if units_targets_pos:
                for x, y in units_targets_pos:
                    arcade.draw_circle_filled(x, y, 8 / self.camera.zoom, arcade.color.GREEN)
