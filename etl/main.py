from utils.logger import Logger
from services.db import Database

if __name__ == "__main__":
    Logger.initialize()
    Database.initialize()