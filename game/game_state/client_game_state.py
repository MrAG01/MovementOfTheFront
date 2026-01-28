from game.map.client_map import ClientMap
from game.player.client_player import ClientPlayer
from utils.space_hash_map import SpaceHashMap


class ClientGameState:
    PHYSIC_ITERATIONS = 4

    def __init__(self, resource_manager, mods_manager, snapshot, self_id):
        self.resource_manager = resource_manager
        self.self_id = self_id
        self.mods_manger = mods_manager
        self.map: ClientMap = ClientMap(resource_manager, mods_manager, snapshot.get("map"))
        self.players: dict[int, ClientPlayer] = self._deserialize_players(snapshot["players"])

        self.units_set = set()
        self.global_units_space_hash_map = SpaceHashMap([], 10, 10)
        self.global_buildings_space_hash_map = SpaceHashMap([], 50, 50)

    def register_unit(self, unit):
        self.units_set.add(unit)
        self.global_units_space_hash_map.add(unit)

    def register_building(self, building):
        self.global_buildings_space_hash_map.add(building)

    def remove_unit(self, unit):
        if unit in self.units_set:
            self.units_set.remove(unit)
        self.global_units_space_hash_map.remove(unit)

    def remove_building(self, building):
        self.global_buildings_space_hash_map.remove(building)

    def _resolve_ones(self):
        for unit in self.units_set:
            closest_units = self.global_units_space_hash_map.get_at(unit.position.x, unit.position.y)
            for resolve_unit in closest_units:
                if unit == resolve_unit:
                    continue
                unit.try_to_resolve_collision(resolve_unit)

    def update_units_logic(self):
        for _ in range(self.PHYSIC_ITERATIONS):
            self._resolve_ones()

    def _deserialize_players(self, data):
        return {int(player_id): ClientPlayer(player_data, self.resource_manager, self.mods_manger, self) for
                player_id, player_data
                in data.items()}

    def update_from_snapshot(self, snapshot):
        players_data = {int(player_id): player_data for player_id, player_data in snapshot["players"].items()}
        for player_id in self.players:
            if player_id in players_data:
                self.players[player_id].update_from_snapshot(players_data[player_id])
        self.map.update_from_snapshot(snapshot["map"])

    # _debug_text = arcade.Text("TOTAL DRAWING TIME: 0", font_size=12, x=0, y=0)

    def update_visual(self, delta_time):
        for player in self.players.values():
            player.update_visual(delta_time)
        self.update_units_logic()

    def draw(self, camera, draw_buildings_alpha):
        # start_time = time.time()

        self.map.draw(camera)
        for player in self.players.values():
            is_self = player.id == self.self_id
            player.draw(camera, draw_buildings_alpha, is_self)

        # end_time = time.time()
        # drawing_time = end_time - start_time
        # x, y, _ = camera.unproject(arcade.Vec2(0, 0))
        # ClientGameState._debug_text.x = x
        # ClientGameState._debug_text.y = y
        # ClientGameState._debug_text.text = f"TOTAL DRAWING TIME: {round(drawing_time, 3)}; MAXIMUM FPS: {round(1 / drawing_time, 1)} "
        # ClientGameState._debug_text.draw()
