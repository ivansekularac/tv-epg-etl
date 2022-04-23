import requests
from models.channel import Channel

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
            return response.json()
        except Exception as err:
            print(err)
            return None

    def get_dates(self) -> list[dict]:
        """Get all dates from mts API.

        Returns:
            list[dict]: List of dates as dicts
        """
        try:
            response = requests.get(self.base_url + "/dates", headers=self.headers)
            return response.json()
        except Exception as err:
            print(err)
            return None

    def get_channels(self) -> list[dict]:
        """Return list of all channels from mts api endpoint.

        Returns:
            list[dict]: List of channels as dicts
        """

        try:
            response = requests.get(self.base_url + "/channel", headers=self.headers)
            # This returns a dict with dicts inside and we need list of dicts
            return [el for el in response.json()]
        except Exception as err:
            print(err)
            return None

    def get_program(self, category: str, date: str) -> list[dict]:
        """Get program items for given channel category and date.

        Args:
            category (str): Channel category ID from mts API
            date (str): Date in format YYYY-MM-DD

        Returns:
            list[dict]: List of channels with program items as dicts
        """
        try:
            params = {"category": category, "date": date}
            response = requests.get(
                self.base_url + "/program", params=params, headers=self.headers
            )
            return response.json()["channels"]
        except Exception as err:
            print(err)
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
            category_channels = self.get_program(category["id"], dates[0]["value"])

            if category_channels:
                for channel in category_channels:
                    channels.append(
                        self.parser.parse_channel(channel, category["text"])
                    )

        return channels
