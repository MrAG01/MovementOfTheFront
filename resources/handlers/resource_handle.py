from abc import ABC, abstractmethod
from resources.resource_packs.resource_packs_error_codes import ResourcePackLoadError
import arcade


class ResourceHandle(ABC):
    def __init__(self, path):
        self.path = path
        self.resource = None
        self._loaded = False

    @abstractmethod
    def _load(self):
        pass

    def _try_load(self):
        try:
            self._load()
        except Exception as error:
            self._loaded = False
            self.resource = None
            raise ResourcePackLoadError(f"Failed to load resource: {self.path}") from error

    def is_loaded(self):
        return self._loaded

    def get(self):
        if not self.is_loaded():
            self._try_load()
        return self.resource
