class SpaceHashMap:
    def __init__(self, objects, chunk_size_x, chunk_size_y=None):
        self.hash_map = {}
        self.rev_map = {}
        self.chunk_size_x = chunk_size_x
        if chunk_size_y is None:
            self.chunk_size_y = chunk_size_x
        else:
            self.chunk_size_y = chunk_size_y

        for object_data in objects:
            self.add(object_data)

        self._last_cache = None

    def get_in_rect(self, rect):
        l, b, r, t = rect

        if t < b:
            t, b = b, t
        if r < l:
            r, l = l, r

        cl = int(l // self.chunk_size_x)
        cr = int(r // self.chunk_size_x)
        ct = int(t // self.chunk_size_y)
        cb = int(b // self.chunk_size_y)

        items = []
        for y in range(cb, ct + 1):
            for x in range(cl, cr + 1):
                dict_key = (x, y)
                if dict_key in self.hash_map:
                    required = []
                    for obj in self.hash_map[dict_key]:
                        ox = obj.position.x
                        oy = obj.position.y
                        # print(ox)
                        if ox >= l and ox <= r and oy >= b and oy <= t:
                            required.append(obj)
                    items.extend(required)
        return items

    def remove(self, object_data):
        true_x, true_y = object_data.position
        space_key = (true_x // self.chunk_size_x, true_y // self.chunk_size_y)
        if object_data in self.rev_map:
            object_data.remove_on_move_callback(self.try_to_update)
            del self.rev_map[object_data]
        if space_key not in self.hash_map:
            return
        data: list = self.hash_map[space_key]
        if object_data in data:
            data.remove(object_data)
        self._last_cache = None

    def try_to_update(self, object_data):
        if object_data not in self.rev_map:
            return
        current_space_key = self.rev_map[object_data]

        x, y = object_data.position.x, object_data.position.y
        space_key = (x // self.chunk_size_x, y // self.chunk_size_y)

        if current_space_key != space_key:
            self.rev_map[object_data] = space_key
            self.hash_map[current_space_key].remove(object_data)
            if space_key in self.hash_map:
                self.hash_map[space_key].append(object_data)
            else:
                self.hash_map[space_key] = [object_data]

    def add(self, object_data):
        true_x, true_y = object_data.position
        space_key = (true_x // self.chunk_size_x, true_y // self.chunk_size_y)
        self.rev_map[object_data] = space_key
        object_data.append_on_move_callback(self.try_to_update)
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
