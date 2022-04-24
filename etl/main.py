from utils.logger import Logger
from services.db import Database
from scrapers.sk import SkScraper
from scrapers.mts import MtsScraper
from orm.models import Channel, Show
import pendulum


def main():
    start = pendulum.now()
    print(f"Started at { start.to_datetime_string() }")

    # Initializers
    Logger.initialize()
    Database.initialize()

    print("Logger and Database initialized")

    # Scrapers
    mts = MtsScraper()
    sk = SkScraper()

    print("Scrapers initialized")
    print("Working...")
    # Scrape data
    mts_channels = mts.scrape()
    sk_channels = sk.scrape()

    print("Scraping completed...")

    # Concat datasets
    channels = mts_channels + sk_channels

    # Clear the database
    Database.drop(Channel)

    print("Database cleared")

    # Save data to database
    Database.insert_all(Channel, channels)
    print(f"{ len(channels) } channels saved to database")

    end = pendulum.now()
    print(f"Finished at { end.now().to_datetime_string() }")
    print(f"Total time: { end.diff(start).in_seconds() } seconds")


if __name__ == "__main__":
    main()
