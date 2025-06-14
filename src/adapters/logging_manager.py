# File: src/adapters/logging_manager.py

import os
import logging
import logging.config
import yaml

class LoggingService:
    """
    Loads logging configuration from src/config/logging.yaml
    and provides three named loggers: request_logger, result_logger, and error_logger.
    """
    def __init__(self, config_path: str = None):
        # 1. Base directory of this file: /app/src/adapters
        base_dir = os.path.abspath(os.path.dirname(__file__))

        # 2. Project root two levels up: /app
        project_root = os.path.abspath(os.path.join(base_dir, os.pardir, os.pardir))

        # 3. Ensure top-level 'logs/' exists
        logs_dir = os.path.join(project_root, 'logs')
        os.makedirs(logs_dir, exist_ok=True)

        # 4. Locate your YAML under src/config/logging.yaml
        default_yaml = os.path.join(base_dir, os.pardir, 'config', 'logging.yaml')
        self.config_path = config_path or os.path.abspath(default_yaml)

        # 5. Load and apply the YAML config
        with open(self.config_path, 'r') as f:
            cfg = yaml.safe_load(f)
        logging.config.dictConfig(cfg)

        # 6. Expose the three loggers defined in your YAML
        self.request_logger = logging.getLogger('request_logger')
        self.result_logger  = logging.getLogger('result_logger')
        self.error_logger   = logging.getLogger('error_logger')

# Instantiate once at import time
logging_service  = LoggingService()
request_logger   = logging_service.request_logger
result_logger    = logging_service.result_logger
error_logger     = logging_service.error_logger