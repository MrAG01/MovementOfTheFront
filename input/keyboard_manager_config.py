from configs.base_config import BaseConfig
from input.str_keys_convertor import StrKeysConvertor


class KeyboardManagerConfig(BaseConfig):
    hotkeys: dict[tuple[int, int], list[str]] = {}

    @classmethod
    def from_dict(cls, data):
        config = cls()
        hks = config.hotkeys
        for name, key_str in data.items():
            dict_key = StrKeysConvertor.convert_string_to_keys(key_str)
            if dict_key not in hks:
                hks[dict_key] = [name]
            else:
                hks[dict_key].append(name)
        return config

    def serialize(self):
        data = {}
        for (key, mods), names in self.hotkeys.items():
            str_key = StrKeysConvertor.convert_keys_to_string(key, mods)
            for name in names:
                data[name] = str_key
        return data
