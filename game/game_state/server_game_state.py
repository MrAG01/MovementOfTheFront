import time

import arcade
from game.actions.events import Event, GameEvents
from game.building.server_building import ServerBuilding
from game.map.server_map import ServerMap
from game.player.server_player import ServerPlayer
from game.unit.server_unit import ServerUnit
from resources.mods.mods_manager.mods_manager import ModsManager
from utils.space_hash_map import SpaceHashMap


class Border:
    def __init__(self):
        pass


class ServerGameState:
    def __init__(self, mods_manager, map):
        self.game_running = False
        self.map: ServerMap = map
        self.mods_manager: ModsManager = mods_manager

        self.players: dict[int, ServerPlayer] = {}

        self.units_set: set[ServerUnit] = set()
        self.units_space_hash_map: SpaceHashMap = SpaceHashMap([], 50, 50)

        self.borders: dict[int, Border]

        self._pending_events: list[Event] = []

    def register_unit(self, unit):
        self.units_set.add(unit)
        self.units_space_hash_map.add(unit)

    def remove_unit(self, unit):
        self.units_set.remove(unit)
        self.units_space_hash_map.remove(unit)

    def update_units_physic(self):

        for unit in self.units_set:
            closest_units = self.units_space_hash_map.get_at(unit.position.x, unit.position.y)
            # print(unit, len(closest_units))
            for resolve_unit in closest_units:
                if unit != resolve_unit:
                    unit.try_to_resolve_collision(resolve_unit)

    def update(self, delta_time):
        #start = time.time()

        self.update_units_physic()
        for player in self.players.values():
            player.update(delta_time)
        self.map.update(delta_time)

        #end = time.time()
        #if end - start:
            #print(f"TOTAL UPDATE TIME: {end - start:.3f}; MAX TICKRATE: {1 / (end - start):.1f}")

    def try_to_destroy_building(self, player_id, data):
        if player_id not in self.players:
            return

        player: ServerPlayer = self.players[player_id]
        player.remove_building(data["building_id"])

    def try_to_add_unit_in_queue(self, player_id, data):
        if player_id not in self.players:
            return
        unit_type = data["unit_type"]
        building_id = data["building_id"]
        self.players[player_id].try_to_add_unit_in_queue(building_id, unit_type)

    def try_to_build(self, player_id, data):
        if player_id not in self.players:
            return

        x, y = int(data["x"]), int(data["y"])
        building_type = data["building_type"]

        biome = self.map.get_biome(x, y)
        if not biome.can_build_on:
            return

        player: ServerPlayer = self.players[player_id]

        building_config = self.mods_manager.get_building(building_type)

        cost_multiplier = biome.build_cost_multiplayer
        actual_cost = building_config.cost * cost_multiplier
        # if player.inventory.try_buy(actual_cost):
        if True:
            time_multiplier = biome.build_time_multiplayer

            building = ServerBuilding.create_new(player, player_id, building_config, time_multiplier, arcade.Vec2(x, y),
                                                 self.mods_manager)
            if "linked_deposit" in data:
                linked_deposit_id = data["linked_deposit"]
                self.map.deposits[linked_deposit_id].try_attach_owned_mine(building)
            player.add_building(building)

    def add_event(self, event):
        self._pending_events.append(event)

    def get_events(self):
        if not self._pending_events:
            return []
        events = self._pending_events.copy()
        self._pending_events.clear()
        return list(map(lambda event: event.serialize(), events))

    def start_game(self, players):
        for player in players.values():
            player.attach_game_state(self)
        self.game_running = True
        self.players = players
        self._pending_events.append(Event(event_type=GameEvents.GAME_STARTED,
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
