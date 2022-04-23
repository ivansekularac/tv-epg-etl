from utils.logger import Logger
from services.db import Database
from scrapers.sk import SkScraper
from scrapers.mts import MtsScraper
from utils.parsers import MtsParser


def main():
    Logger.initialize()
    Database.initialize()


if __name__ == "__main__":
    main()
