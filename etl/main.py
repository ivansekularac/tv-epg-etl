from utils.logger import Logger
from services.db import Database


def main():
    Logger.initialize()
    Database.initialize()


if __name__ == "__main__":
    main()
