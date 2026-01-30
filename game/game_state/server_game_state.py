import arcade
from game.actions.events import Event, GameEvents
from game.building.server_building import ServerBuilding
from game.map.server_map import ServerMap
from game.player.server_player import ServerPlayer
from game.unit.server_unit import ServerUnit
from game.unit.unit_config import UnitConfig
from resources.mods.mods_manager.mods_manager import ModsManager
from utils.space_hash_map import SpaceHashMap


class ServerGameState:
    PHYSIC_ITERATIONS = 4

    def __init__(self, mods_manager, map):
        self.game_running = False
        self.map: ServerMap = map
        self.mods_manager: ModsManager = mods_manager

        self.players: dict[int, ServerPlayer] = {}

        self.units_set: set[ServerUnit] = set()
        self.units_space_hash_map: SpaceHashMap = SpaceHashMap([], 25, 25)

        self.buildings_space_hash_map: SpaceHashMap = SpaceHashMap([], 25, 25)

        self._pending_events: list[Event] = []

        self.day_night_cycle = 60
        self.day_night_cycle_state = 0

    def try_to_set_building_enabled(self, player_id, data):
        if player_id not in self.players:
            return
        player: ServerPlayer = self.players[player_id]
        if "building_id" not in data:
            return
        building_id = data["building_id"]
        if "state" not in data:
            return
        state = data["state"]
        player.try_to_set_building_enabled(building_id, state)

    def register_unit(self, unit):
        self.units_set.add(unit)
        self.units_space_hash_map.add(unit)

    def register_building(self, building):
        self.buildings_space_hash_map.add(building)

    def remove_unit(self, unit):
        self.units_set.remove(unit)
        self.units_space_hash_map.remove(unit)

    def remove_building(self, building):
        self.buildings_space_hash_map.remove(building)

    def _resolve_ones(self, units_make_damage_map):
        for unit in self.units_set:
            closest_units = self.units_space_hash_map.get_at(unit.position.x, unit.position.y)
            make_damage = set()
            for resolve_unit in closest_units:
                if unit == resolve_unit:
                    continue
                scan_attack, ocan_attack = unit.check_for_attack(resolve_unit)
                if scan_attack:
                    make_damage.add(resolve_unit)
                if ocan_attack:
                    if resolve_unit in units_make_damage_map:
                        units_make_damage_map[resolve_unit].add(unit)
                    else:
                        units_make_damage_map[resolve_unit] = set()
                        units_make_damage_map[resolve_unit].add(unit)

                unit.try_to_resolve_collision(resolve_unit)
            if make_damage:
                if unit in units_make_damage_map:
                    units_make_damage_map[unit] |= make_damage
                else:
                    units_make_damage_map[unit] = make_damage

    def update_units_logic(self):
        make_damage_map = {}
        for _ in range(self.PHYSIC_ITERATIONS):
            self._resolve_ones(make_damage_map)

        for unit in self.units_set:
            closest_buildings = self.buildings_space_hash_map.get_at(unit.position.x, unit.position.y)
            buildings_to_damage = set()
            for building in closest_buildings:
                if unit.can_attack_building(building):
                    buildings_to_damage.add(building)
            if not buildings_to_damage:
                continue
            if unit in make_damage_map:
                make_damage_map[unit] |= buildings_to_damage
            else:
                make_damage_map[unit] = buildings_to_damage

        for unit, damage_to in make_damage_map.items():
            spread = len(damage_to)
            damage = unit.unit_config.units_damage
            spread_damage = damage / spread
            for object_to_damage in damage_to:
                object_to_damage.get_damage(spread_damage)

    def update(self, delta_time):
        # start = time.time()
        #self.day_night_cycle_state +=

        self.update_units_logic()
        for player in self.players.values():
            player.update(delta_time)
        self.map.update(delta_time)

        # end = time.time()
        # if end - start:
        # print(f"TOTAL UPDATE TIME: {end - start:.3f}; MAX TICKRATE: {1 / (end - start):.1f}")

    def try_to_set_building_production(self, player_id, data):
        if player_id not in self.players:
            return

        building_id = data["building_id"]
        production_index = data["production_index"]
        player: ServerPlayer = self.players[player_id]
        if player.death:
            return
        player.try_to_set_building_production(building_id, production_index)

    def try_to_destroy_building(self, player_id, data):
        if player_id not in self.players:
            return

        player: ServerPlayer = self.players[player_id]
        if player.death:
            return
        player.remove_building(data["building_id"])

    def try_to_add_unit_in_queue(self, player_id, data):
        if player_id not in self.players:
            return
        unit_type = data["unit_type"]
        building_id = data["building_id"]
        player = self.players[player_id]
        if player.death:
            return
        player.try_to_add_unit_in_queue(building_id, unit_type)

    def try_to_make_new_unit_path(self, player_id, data):
        if player_id not in self.players:
            return
        unit_id = data["unit_id"]
        new_path = data["path"]
        player = self.players[player_id]
        if player.death:
            return
        player.try_to_make_new_unit_path(unit_id, new_path)

    def try_to_build(self, player_id, data):
        if player_id not in self.players:
            return

        x, y = int(data["x"]), int(data["y"])
        building_type = data["building_type"]

        biome = self.map.get_biome(x, y)
        if not biome.can_build_on:
            return

        player: ServerPlayer = self.players[player_id]
        if player.death:
            return

        building_config = self.mods_manager.get_building(building_type)
        if not building_config.can_build:
            return

        units_close = self.units_space_hash_map.get_at(x, y)

        for unit in units_close:
            config: UnitConfig = unit.unit_config
            if not config.can_build_buildings:
                continue
            delta: arcade.Vec2 = (arcade.Vec2(x, y) - unit.position)
            distance_sqr = delta.length_squared()
            if distance_sqr <= config.buildings_build_range ** 2:
                break
        else:
            return

        # cost_multiplier = biome.build_cost_multiplayer
        actual_cost = building_config.cost  # * cost_multiplier
        if player.inventory.subs(actual_cost):
            time_multiplier = biome.build_time_multiplayer

            building = ServerBuilding.create_new(player, player_id, building_config, time_multiplier, arcade.Vec2(x, y),
                                                 self.mods_manager)
            if "linked_deposit" in data:
                linked_deposit_id = data["linked_deposit"]
                self.map.deposits[linked_deposit_id].try_attach_owned_mine(building)
            self.register_building(building)
            player.add_building(building)

    def add_event(self, event):
        self._pending_events.append(event)

    def get_events(self):
        if not self._pending_events:
            return []
        events = self._pending_events.copy()
        self._pending_events.clear()
        return list(map(lambda event: event.serialize(), events))

    def _check_for_game_finish(self):
        alive_players = [player for player in self.players.values() if not player.death]
        if len(alive_players) == 1 and len(self.players) > 1:
            self.add_event(Event(event_type=GameEvents.GAME_OVER,
                                 data={"winner": alive_players[0].player_id}))

    def player_base_destroyed(self, player: ServerPlayer):
        self.add_event(Event(event_type=GameEvents.PLAYER_DIED,
                             data=player.player_id))
        self._check_for_game_finish()

    def start_game(self, players):
        for player in players.values():
            player.attach_game_state(self)
        self.game_running = True
        self.players = players

        for player in self.players.values():
            player.generate_town_hall(self.mods_manager)

        self.add_event(Event(event_type=GameEvents.GAME_STARTED,
                             data=self.serialize_static()))

    def serialize_static(self):
        return {
            "map": self.map.serialize_static() if self.map is not None else None,
            "players": {player_id: player.serialize_static() for player_id, player in self.players.items()}
        }

    def serialize_dynamic(self):
        return {"events": self.get_events(),
                "data": {
                    "game_running": self.game_running,
                    "players": {player_id: player.serialize_dynamic() for player_id, player in self.players.items() if
                                player.is_dirty()},
                    "map": self.map.serialize_dynamic()
                }}
