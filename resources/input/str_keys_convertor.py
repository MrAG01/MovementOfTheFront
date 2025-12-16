from pyglet.window import key


class StrKeysConvertor:
    _MODIFIERS_TO_STR = {}
    _STR_TO_MODIFIERS = {}

    _MODIFIERS_TO_KEYS = {}
    _KEYS_TO_MODIFIERS = {}

    _KEYS_TO_STR = {}

    @classmethod
    def init(cls):
        cls._STR_TO_MODIFIERS = {
            "CTRL": key.MOD_CTRL,
            "SHIFT": key.MOD_SHIFT,
            "ALT": key.MOD_ALT,
            "CMD": key.MOD_COMMAND,
            "WIN": key.MOD_COMMAND
        }
        cls._MODIFIERS_TO_KEYS = {
            key.MOD_SHIFT: key.LSHIFT,
            key.MOD_ALT: key.LALT,
            key.MOD_CTRL: key.LCTRL,
            key.MOD_COMMAND: key.LCOMMAND
        }
        cls._KEYS_TO_MODIFIERS = {v: k for k, v in cls._MODIFIERS_TO_KEYS.items()}
        cls._MODIFIERS_TO_STR = {v: k for k, v in cls._STR_TO_MODIFIERS.items()}
        cls._KEYS_TO_STR = {v: k for k, v in key._key_names.items()}

    @staticmethod
    def modifiers_to_str(modifiers):
        modifiers_str_parts = []
        for code, name in StrKeysConvertor._MODIFIERS_TO_STR.items():
            if modifiers & code == code:
                modifiers_str_parts.append(StrKeysConvertor._MODIFIERS_TO_STR[code] + "+")

        return "".join(modifiers_str_parts)

    @staticmethod
    def str_to_modifier(str_modifier):
        modifier = StrKeysConvertor._STR_TO_MODIFIERS.get(str_modifier, "UNKNOWN_KEY")
        if modifier in StrKeysConvertor._MODIFIERS_TO_KEYS:
            modifier = StrKeysConvertor._MODIFIERS_TO_KEYS[modifier]
        return modifier

    @staticmethod
    def convert_string_to_keys(bind):
        data = bind.upper().split("+")
        if len(data) > 1:
            modifiers = 0
            for modifier_str in data[:-1]:
                modifiers |= StrKeysConvertor.str_to_modifier(modifier_str)
        else:
            modifiers = 0
        key_code = StrKeysConvertor._KEYS_TO_STR[data[-1]]
        return key_code, modifiers

    @staticmethod
    def convert_keys_to_string(key_code, modifiers):
        if modifiers in StrKeysConvertor._KEYS_TO_MODIFIERS:
            modifiers = StrKeysConvertor._KEYS_TO_MODIFIERS[modifiers]
        return StrKeysConvertor.modifiers_to_str(modifiers) + key.symbol_string(key_code)


StrKeysConvertor.init()
