class NotificationMixin:
    def __init__(self):
        self._sending_enabled = True
        self._has_changes = False
        self._listeners = []

    def add_listener(self, listener_callback, notify_immediately=True):
        self._listeners.append(listener_callback)
        if notify_immediately:
            listener_callback(self)

    def remove_listener(self, listener_callback):
        if listener_callback in self._listeners:
            self._listeners.remove(listener_callback)

    def notify_listeners(self):
        if self._sending_enabled:
            for callback in self._listeners:
                callback(self)
            self._has_changes = False
        else:
            self._has_changes = True

    def disable_notifications(self):
        self._sending_enabled = False

    def enable_notifications(self):
        self._sending_enabled = True
        if self._has_changes:
            self.notify_listeners()

    def has_listeners(self):
        return len(self._listeners) != 0

    def clear_listeners(self):
        self._listeners.clear()
