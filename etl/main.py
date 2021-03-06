import logging

import pendulum

from orm.models import Channel, Date
from scrapers.mts import MTS
from scrapers.sbb import SBB
from services.db import Database
from utils import helpers
from utils.logger import Logger
from utils.parsers import DateParser


def main():
    start = pendulum.now()
    print(f"Started at { start.to_datetime_string() }")

    # Initializers
    Logger.initialize()
    Database.initialize()

    print("Logger and Database initialized")
    logging.info(f"Started at { start.to_datetime_string() }")

    # Instantiate scrapers
    mts = MTS()
    sbb = SBB()
    print("Scrapers initialized")
    logging.info("Scrapers initialized")
    print("Working...")
    # Scrape data
    mts_channels = mts.scrape()
    sbb_channels = sbb.scrape()

    print("Scraping completed...")
    logging.info("Scraping completed...")

    # Concat datasets
    channels = mts_channels + sbb_channels

    # Prepare dates data
    start_dt, end_dt = helpers.min_max_date(channels[:20])
    dates = helpers.daterange(start_dt, end_dt)
    parsed_dates = [DateParser.parse(date) for date in dates]

    # Clear the database
    Database.drop(Channel)
    Database.drop(Date)

    print("Database cleared\nWriting to database...")

    # Save data to database
    Database.insert_all(Channel, channels)
    print(f"{ len(channels) } channels saved to database")

    Database.insert_all(Date, parsed_dates)
    print(f"{ len(parsed_dates) } dates saved to database")

    end = pendulum.now()
    print(f"Finished at { end.now().to_datetime_string() }")
    print(f"Total time: { end.diff(start).in_seconds() } seconds")

    logging.info(
        f"Finished at { end.now().to_datetime_string() } (Runtime: { end.diff(start).in_seconds() } seconds)"
    )

if __name__ == "__main__":
    main()
