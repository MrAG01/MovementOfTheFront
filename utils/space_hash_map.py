class SpaceHashMap:
    def __init__(self, objects, chunk_size_x, chunk_size_y=None):
        self.hash_map = {}
        self.chunk_size_x = chunk_size_x
        if chunk_size_y is None:
            self.chunk_size_y = chunk_size_x
        else:
            self.chunk_size_y = chunk_size_y

        for object_data in objects.values():
            self.add(object_data)

        self._last_cache = None

    def remove(self, object_data):
        true_x, true_y = object_data.position
        space_key = (true_x // self.chunk_size_x, true_y // self.chunk_size_y)
        if space_key not in self.hash_map:
            return
        data: list = self.hash_map[space_key]
        if object_data in data:
            data.remove(data)
        self._last_cache = None

    def add(self, object_data):
        true_x, true_y = object_data.position
        space_key = (true_x // self.chunk_size_x, true_y // self.chunk_size_y)
        if space_key in self.hash_map:
            self.hash_map[space_key].append(object_data)
        else:
            self.hash_map[space_key] = [object_data]
        self._last_cache = None

    def _get_at_true(self, middle_chunk_x, middle_chunk_y):
        objects = []
        middle_chunk_x, middle_chunk_y = int(middle_chunk_x), int(middle_chunk_y)
        for chunk_y in range(middle_chunk_y - 1, middle_chunk_y + 2):
            for chunk_x in range(middle_chunk_x - 1, middle_chunk_x + 2):
                objects.extend(self.hash_map.get((chunk_x, chunk_y), []))

        return objects

    def get_at(self, x, y):
        middle_chunk_x, middle_chunk_y = (x // self.chunk_size_x, y // self.chunk_size_y)
        if self._last_cache is None:
            data = self._get_at_true(middle_chunk_x, middle_chunk_y)
            self._last_cache = ((middle_chunk_x, middle_chunk_y), data)
            return data
        else:
            space_key, data = self._last_cache
            if (middle_chunk_x, middle_chunk_y) == space_key:
                return data
            else:
                data = self._get_at_true(middle_chunk_x, middle_chunk_y)
                self._last_cache = ((middle_chunk_x, middle_chunk_y), data)
                return data