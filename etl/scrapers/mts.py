import logging
from typing import Optional

import requests
from orm.models import Channel, Show
from utils.parsers import MtsParser


class MtsScraper:
    def __init__(self):
        self.base_url = "https://mts.rs/oec/epg"
        self.headers = {
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        }
        self.parser = MtsParser()

    def get_categories(self) -> list[dict]:
        """Get all categories from mts API.

        Returns:
            list[dict]: List of categories as dicts
        """
        try:
            response = requests.get(self.base_url + "/categories", headers=self.headers)
            logging.info("Categories fetched from mts API")
            return response.json()
        except Exception as err:
            logging.error(err, exc_info=True)
            return None

    def get_dates(self) -> list[dict]:
        """Get all dates from mts API.

        Returns:
            list[dict]: List of dates as dicts
        """
        try:
            response = requests.get(self.base_url + "/dates", headers=self.headers)
            logging.info("Dates fetched from mts API")
            return response.json()
        except Exception as err:
            logging.error(err, exc_info=True)
            return None

    def get_channels(self) -> list[dict]:
        """Return list of all channels from mts api endpoint.

        Returns:
            list[dict]: List of channels as dicts
        """

        try:
            response = requests.get(self.base_url + "/channel", headers=self.headers)
            logging.info("Channels fetched from mts API")
            # This returns a dict with dicts inside and we need list of dicts
            return [el for el in response.json()]
        except Exception as err:
            logging.error(err, exc_info=True)
            return None

    def get_shows(
        self,
        category_id: Optional[str] = None,
        category_name: Optional[str] = None,
        date: Optional[str] = None,
    ) -> list[dict]:
        """Get program items for given channel category and date.

        Args:
            category_id (str): Category ID (optional)
            category_name (str): Category name (optional)
            date (str): Date in format YYYY-MM-DD (optional)

        Returns:
            list[dict]: List of channels with program items as dicts
        """
        try:
            params = {"channel-type": "tv", "category": category_id, "date": date}
            response = requests.get(
                self.base_url + "/program", params=params, headers=self.headers
            )
            logging.info(
                f"EPG for channels in category: { category_name if category_name else 'All'} fetched."
            )
            return response.json().get("channels", [])
        except Exception as err:
            logging.error(err, exc_info=True)
            return None

    def prepare_channels(self, shows: list[Show]) -> list[Channel]:
        """Prepare channels for saving to database.

        Returns:
            list[Channel]: List of channels as model objects
        """
        categories = self.get_categories()
        dates = self.get_dates()

        channels = []

        for category in categories:
            category_channels = self.get_shows(
                category["id"], category["text"], dates[0]["value"]
            )

            if category_channels:
                for channel in category_channels:
                    matching_shows = [
                        show for show in shows if show.oid == int(channel["id"])
                    ]

                    if matching_shows:
                        channels.append(
                            self.parser.parse_channel(
                                channel, category["text"], matching_shows
                            )
                        )

        logging.info(f"{ len(channels) } channels prepared for database.")

        return channels

    def prepare_shows(self) -> list[Show]:
        """Prepare shows for saving to database.

        Returns:
            list[Show]: List of shows as model objects
        """
        dates = self.get_dates()

        shows = []

        for date in dates:
            data = self.get_shows(date=date["value"])

            for channel in data:
                for show in channel["items"]:
                    shows.append(self.parser.parse_show(show))

        logging.info(f"{len(shows)} shows prepared for database.")
        return shows

    def scrape(self) -> dict[list]:
        """Scrape data from mts API.

        Returns:
            dict[list]: Dictionary with lists of channels and shows
        """
        shows = self.prepare_shows()
        channels = self.prepare_channels(shows)
        logging.info(
            f"{len(channels)} channels with {len(shows)} embedded shows scraped."
        )
        return channels
