import arcade
from game.actions.events import Event, GameEvents
from game.map.client_map import ClientMap
from game.map.map_generation_settings import MapGenerationSettings
from game.map.map_generator import MapGenerator
from game.map.server_map import ServerMap


class ServerGameState:
    def __init__(self, map):
        self.game_running = False
        self.map: ServerMap = map

        self._pending_events: list[Event] = []

    def add_event(self, event):
        self._pending_events.append(event)

    def get_events(self):
        if not self._pending_events:
            return []
        events = self._pending_events.copy()
        self._pending_events.clear()
        return list(map(lambda event: event.serialize(), events))

    def start_game(self):
        self.game_running = True
        self._pending_events.append(Event(event_type=GameEvents.GAME_STARTED,
                                          data=self.serialize_static()))

    def serialize_full(self):
        return self.serialize_static() | self.serialize_dynamic()

    def serialize_static(self):
        return {
            "map": self.map.serialize() if self.map is not None else None
        }

    def serialize_dynamic(self):
        return {"game_running": self.game_running}

    def serialize(self):
        return {
            "events": self.get_events(),
            "data": self.serialize_dynamic()
        }


class ClientGameState:
    def __init__(self, resource_manager, snapshot):
        self.map: ClientMap = ClientMap(resource_manager, snapshot.get("map"))

    def update_from_snapshot(self, snapshot):
        pass

    def draw(self):
        self.map.draw()
