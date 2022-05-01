import logging
import requests
from orm.models import Channel, Show
from utils.parsers import ParserMTS


class MTS:
    def __init__(self):
        self.base_url = "https://mts.rs/oec/epg"
        self.headers = {
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        }
        self.parser = ParserMTS()

    def fetch_categories(self) -> list[dict]:
        """Get all categories from mts API.

        Returns:
            list[dict]: List of categories as dicts
        """
        try:
            response = requests.get(self.base_url + "/categories", headers=self.headers)
            logging.info(f"{len(response.json())} categories fetched from mts API")
            return response.json()
        except Exception as err:
            logging.error(err, exc_info=True)
            return None

    def fetch_dates(self) -> list[dict]:
        """Get all dates from mts API.

        Returns:
            list[dict]: List of dates as dicts
        """
        try:
            response = requests.get(self.base_url + "/dates", headers=self.headers)
            logging.info(f"{ len(response.json()) } dates fetched from mts API")
            return response.json()
        except Exception as err:
            logging.error(err, exc_info=True)
            return None

    def fetch_channels(self) -> list[dict]:
        """Fetch channels from mts API.

        Returns:
            list[dict]: List of channels as dicts
        """
        categories = self.fetch_categories()
        channels = []

        try:
            for category in categories:
                # Skip adult category
                if category["text"] == "Za odrasle":
                    continue

                params = {
                    "category": category["id"],
                    "channel-type": "tv",
                }
                response = requests.get(
                    self.base_url + "/program", params=params, headers=self.headers
                )

                for item in response.json().get("channels", []):
                    # skip mts promo channel
                    if item["name"] == "iris TV promo":
                        continue

                    channels.append(
                        {
                            "id": item["id"],
                            "name": item["name"],
                            "image": item["image"],
                            "category": category["text"],
                        }
                    )
        except Exception as err:
            logging.error(err, exc_info=True)
            return None

        logging.info(f"Fetched { len(channels) } channels from mts API")
        return channels

    def fetch_data(self) -> dict[list]:
        """Fetch channels & shows data from API

        Returns:
            dict[list]: Dict with channels and shows data
        """
        channels = self.fetch_channels()
        dates = self.fetch_dates()

        shows = []

        try:
            # Fetch shows for each channel for all dates
            for date in dates:
                params = {
                    "channel-type": "tv",
                    "date": date["value"],
                }
                response = requests.get(
                    self.base_url + "/program", params=params, headers=self.headers
                )

                for item in response.json().get("channels", []):
                    shows.extend(item["items"])

        except Exception as err:
            logging.error(err, exc_info=True)
            return None

        logging.info(
            f"{ len(channels) } channels with total { len(shows) } shows fetched from MTS API"
        )
        return {"channels": channels, "shows": shows}

    def parse_shows(self, data: list[dict]) -> list[Show]:
        """Parse shows data and return list of Show objects

        Args:
            data (list[dict]): List of shows data as dicts

        Returns:
            list[Show]: List of Show objects
        """
        parsed = []

        for item in data:
            parsed.append(self.parser.parse_show(item))

        return parsed

    def parse_channels(self, data: list[dict], shows: list[Show]) -> list[Channel]:
        """Parse channels data and return list of Channel objects

        Args:
            data (list[dicts]): List of channels data as dicts
            shows (list[Show]): List of Show objects

        Returns:
            list[Channel]: List of Channel objects
        """
        parsed = []

        for item in data:
            matching_shows = [show for show in shows if show.oid == int(item["id"])]
            parsed.append(self.parser.parse_channel(item, matching_shows))

        logging.info(
            f"{ len(parsed) } channels parsed from mts API with total of { len(shows) } shows"
        )
        return parsed

    def scrape(self) -> list[Channel]:
        """Scrape data from API

        Returns:
            list[Channel]: List of Channel objects with their respective shows
        """

        data = self.fetch_data()
        shows = self.parse_shows(data["shows"])
        channels = self.parse_channels(data["channels"], shows)
        return channels
