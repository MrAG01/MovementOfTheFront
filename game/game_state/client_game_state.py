from game.map.client_map import ClientMap
from game.player.client_player import ClientPlayer


class ClientGameState:
    def __init__(self, resource_manager, mods_manager, snapshot):
        self.resource_manager = resource_manager
        self.mods_manger = mods_manager
        self.map: ClientMap = ClientMap(resource_manager, mods_manager, snapshot.get("map"))
        self.players: dict[int, ClientPlayer] = self._deserialize_players(snapshot["players"])
        self.teams = snapshot["teams"]

    def _deserialize_players(self, data):
        return {int(player_id): ClientPlayer(player_data, self.resource_manager, self.mods_manger) for
                player_id, player_data
                in data.items()}

    def update_from_snapshot(self, snapshot):
        players_data = {int(player_id): player_data for player_id, player_data in snapshot["players"].items()}
        for player_id in self.players:
            if player_id in players_data:
                self.players[player_id].update_from_snapshot(players_data[player_id])
        self.map.update_from_snapshot(snapshot["map"])

    def draw(self, camera):
        self.map.draw(camera)
        for player in self.players.values():
            player.draw(camera)
