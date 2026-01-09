import threading
from weakref import WeakValueDictionary
from game.actions.events import Event


class NetworkObject:
    _next_object_id = 1
    _thread_locker = threading.Lock()
    _network_objects = WeakValueDictionary()

    def __init__(self, owner_id):
        with NetworkObject._thread_locker:
            self._self_id = NetworkObject._next_object_id
            NetworkObject._next_object_id += 1
            self._owner_id = owner_id
            self._pending_events: list[Event] = []
            NetworkObject._network_objects[self._self_id] = self

    @property
    def id(self):
        return self._self_id

    def change_owner(self, new_owner_id):
        self._owner_id = new_owner_id

    @classmethod
    def get_object(cls, id):
        return cls._network_objects.get(id)

    @classmethod
    def get_network_objects(cls):
        return dict(cls._network_objects)

    @property
    def owner(self):
        return self._owner_id

    def add_event(self, event: Event):
        self._pending_events.append(event)

    def get_events(self) -> list[dict]:
        if not self._pending_events:
            return []
        events = self._pending_events.copy()
        self._pending_events.clear()
        return list(map(lambda event: event.serialize(), events))

    def serialize(self):
        return {
            "id": self._self_id,
            "owner_id": self._owner_id
        }

    def __repr__(self):
        return f"{type(self).__name__}(id={self._self_id}, owner={self._owner_id})"
