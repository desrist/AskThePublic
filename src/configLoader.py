import yaml
import os

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

config = load_config(os.path.join(os.path.dirname(__file__), 'config.yaml'))
