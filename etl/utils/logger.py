import logging
from datetime import datetime


def initialize():
    """Logger setup and initialization"""
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"logs/{now}.log"
    logging.basicConfig(
        filename=file_name,
        filemode="w",
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
    )
    logging.getLogger()
