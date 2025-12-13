from game.game_state import ClientGameState
from network.client.network_connection import NetworkConnection


class InputHandler:
    pass


class GameClient:
    def __init__(self):
        self.connected = NetworkConnection()

        self.game_state = ClientGameState()
        self.player_id = None

        self.input_handler = InputHandler()
        self.commands_queue = None

        self.last_message_time = 0
        self.server_tick = 0

    def connect(self, ip, port):
        callback = self.connected.connect(ip, port)
        if not callback["success"]:
            return callback

