import logging
from typing import Optional

import requests
from models.channel import Channel
from models.show import Show
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

    def get_program(
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
            params = {"category": category_id, "date": date}
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

    def prepare_channels(self) -> list[Channel]:
        """Prepare channels for saving to database.

        Returns:
            list[Channel]: List of channels as model objects
        """
        categories = self.get_categories()
        dates = self.get_dates()

        channels = []

        for category in categories:
            category_channels = self.get_program(
                category["id"], category["text"], dates[0]["value"]
            )

            if category_channels:
                for channel in category_channels:
                    channels.append(
                        self.parser.parse_channel(channel, category["text"])
                    )

        logging.info(f"{len(channels)} channels prepared for database.")

        return channels

    def prepare_shows(self) -> list[Show]:
        """Prepare shows for saving to database.

        Returns:
            list[Show]: List of shows as model objects
        """
        dates = self.get_dates()

        shows = []

        for date in dates:
            data = self.get_program(date=date["value"])

            for el in data:
                shows.extend([self.parser.parse_show(item) for item in el["items"]])

        logging.info(f"{len(shows)} shows prepared for database.")
        return shows