import yaml
import logging.config
from pathlib import Path


class AppConfigLoader:
    def __init__(self, config_path: str = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Detecta la raíz del proyecto de forma relativa a este archivo
            self.config_path = Path(__file__).resolve().parent.parent.parent / "application.yaml"
        self.config = self._load_config()
        self._configure_logging()

    def _load_config(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        with self.config_path.open("r") as f:
            return yaml.safe_load(f)

    def _configure_logging(self):
        logging_config = self.config.get("logging", {})
        if logging_config:
            logging.config.dictConfig(logging_config)
        else:
            logging.basicConfig(level=logging.INFO)
            logging.warning("Logging config not found. Using basic logging setup.")

    def get_flask_config(self):
        return self.config.get("app", {}).get("flask", {})
    
    def get_nsjail_config(self):
        return self.config.get("nsjail", {})

    def get_allowed_commands(self):
        return self.config.get("app", {}).get("allowed_commands", [])

    def get_config(self):
        return self.config