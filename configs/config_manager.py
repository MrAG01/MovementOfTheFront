import json
from utils.os_utils import generate_dirs


class ConfigManager:
    def __init__(self, path):
        self.configs_folder_path = path
        self._config_classes = {}
        self._config_registry = {}

    def register_config(self, config_name, config_class):
        if self.has_config(config_name):
            return self.get_config(config_name)
        self._config_classes[config_name] = config_class
        config = self._load_config(config_name, config_class)
        self._config_registry[config_name] = config
        return config

    def register_config_instance(self, config_name, config_instance):
        self._config_registry[config_name] = config_instance
        return config_instance

    def _load_config(self, config_name, config_class):
        try:
            path = f"{self.configs_folder_path}/{config_name}.json"
            with open(path, 'r', encoding='utf-8') as file:
                config = config_class.from_dict(json.load(file))
        except (FileNotFoundError, PermissionError, json.JSONDecodeError):
            config = config_class.get_default()
        except Exception as error:
            print(f"Unexpected error: {error}")
            config = config_class.get_default()
        return config

    def save_config(self, config_name):
        if config_name not in self._config_registry:
            raise KeyError(f"Config '{config_name}' not registered")

        config = self._config_registry[config_name]
        config_path = f"{self.configs_folder_path}/{config_name}.json"
        try:
            generate_dirs(config_path)
            with open(config_path, 'w', encoding='utf-8') as file:
                json.dump(config.serialize(), file, indent=2)
        except Exception as error:
            print(f"Error saving config '{config_name}': {error}")

    def save_all(self):
        for name in self._config_registry:
            self.save_config(name)

    def has_config(self, name):
        return name in self._config_registry

    def get_config(self, name):
        return self._config_registry.get(name)
