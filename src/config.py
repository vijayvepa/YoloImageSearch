import yaml
from pathlib import Path

def load_config(config_path="configs/default.yaml"):
		"""
		Load configuration from a YAML file.
		"""
		with open(Path(config_path), 'r') as file:
				config = yaml.safe_load(file)
		return config

def save_config(config, config_path="configs/default.yaml"):
		"""
		Save configuration to a YAML file.
		"""
		with open(Path(config_path), 'w') as file:
				yaml.safe_dump(config, file)