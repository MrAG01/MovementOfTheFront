from abc import ABC, abstractmethod
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
            print(f"Error loading {self.__class__.__name__} from '{self.path}': {error}")
            self._loaded = False
            self.resource = None

    def is_loaded(self):
        return self._loaded

    def get(self):
        if not self.is_loaded():
            self._try_load()
        return self.resource

