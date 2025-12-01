from game.game_state import GameState


class GameClient:
    def __init__(self):
        self.real_game_state: GameState = None
        self.predicted_game_state: GameState = None

    def update(self, delta_time):
        self.predicted_game_state.update(delta_time)

    def draw(self):
        self.predicted_game_state.draw()

    def _reсv_game_state_from_server(self):
        ...
