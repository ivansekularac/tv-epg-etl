import logging
from datetime import datetime
from os import path


class Logger:
    @staticmethod
    def initialize():
        """Logger setup and initialization"""
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        logs_dir = path.abspath(path.join(path.dirname(__file__), "..", "..", "logs"))
        file_name = f"{now}.log"
        file_path = path.join(logs_dir, file_name)
        logging.basicConfig(
            filename=file_path,
            filemode="w",
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=logging.INFO,
        )
        logging.getLogger()
        logging.info(f"Logging initialized to {file_path}")
