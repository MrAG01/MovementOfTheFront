from game.map.client_map import ClientMap
from game.player.client_player import ClientPlayer


class ClientGameState:
    def __init__(self, resource_manager, mods_manager, snapshot):
        self.resource_manager = resource_manager
        self.mods_manger = mods_manager
        self.map: ClientMap = ClientMap(resource_manager, mods_manager, snapshot.get("map"))
        self.players: dict[int, ClientPlayer] = self._deserialize_players(snapshot["players"])

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

    def draw(self, camera, draw_buildings_alpha):
        # start_time = time.time()

        self.map.draw(camera)
        for player in self.players.values():
            player.draw(camera, draw_buildings_alpha)

        # end_time = time.time()
        # drawing_time = end_time - start_time
        # x, y, _ = camera.unproject(arcade.Vec2(0, 0))
        # ClientGameState._debug_text.x = x
        # ClientGameState._debug_text.y = y
        # ClientGameState._debug_text.text = f"TOTAL DRAWING TIME: {round(drawing_time, 3)}; MAXIMUM FPS: {round(1 / drawing_time, 1)} "
        # ClientGameState._debug_text.draw()
