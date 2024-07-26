import yaml
import os

class config:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, dict):
                value = config(**value)
            setattr(self, key, value)

def yaml_to_class(yaml_str, cls):
    config_data = yaml.safe_load(yaml_str)
    return cls(**config_data)

script_dir = os.path.dirname(os.path.abspath(__file__))
yaml_file_path = os.path.join(script_dir, "config.yml")

with open(yaml_file_path, "r", encoding="utf8") as f:
    Config = yaml_to_class(f.read(), config)