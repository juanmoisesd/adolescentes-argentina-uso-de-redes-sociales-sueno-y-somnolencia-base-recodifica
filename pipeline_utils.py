import os
import logging
import json
from datetime import datetime
from pathlib import Path

def setup_logger(name, log_file="logs/execution.log"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    return logger

def get_config():
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            return json.load(f)
    return {}

def update_progress(phase, data):
    progress_file = f"logs/progress_phase_{phase}.json"
    with open(progress_file, "w") as f:
        json.dump(data, f, indent=2)

def get_zenodo_token():
    return os.getenv("ZENODO_TOKEN") or os.getenv("ZENODO_SANDBOX_TOKEN")
