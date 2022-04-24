import logging

import requests
from decouple import config
from orm.models import Channel, Show
from utils.parsers import SkParser
import pendulum


class SkScraper:
    def __init__(self) -> None:
        self.base_url = "https://api-web.ug-be.cdn.united.cloud"
        self.parser = SkParser()
        self._bearer = None

    def get_auth_token(self) -> None:
        """Fetch Bearer token from SK API

        Returns:
            str: Bearer token
        """

        headers = {
            "Accept": "application/json",
            "Authorization": "Basic " + config("SK_BASIC_TOKEN"),
        }
        params = {"grant_type": "client_credentials"}

        try:
            response = requests.post(
                self.base_url + "/oauth/token", params=params, headers=headers
            )
            logging.info(f"Bearer token successfully fetched from SK API")

            self._bearer = response.json()["access_token"]

        except Exception as err:
            logging.error(err, exc_info=True)

        """Fetch all channel IDs from SK API

        Returns:
            list[str]: List 
        """

        if not self._bearer:
            self.get_auth_token()

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer { self._bearer }",
        }
        params = {"imageSize": "S", "communityIdentifier": "sk_rs", "languageId": "404"}

        try:
            response = requests.get(
                self.base_url + "/v2/public/channels", params=params, headers=headers
            )
            logging.info(f"Channels successfully fetched from SK API")
            return response.json()
        except Exception as err:
            logging.error(err, exc_info=True)
            return None

    def get_channels(self) -> list[dict]:
        """Fetch all channels from SK API

        Returns:
            list[dict]: List of channels
        """

        if not self._bearer:
            self.get_auth_token()

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer { self._bearer }",
        }
        params = {"imageSize": "S", "communityIdentifier": "sk_rs", "languageId": "404"}

        try:
            response = requests.get(
                self.base_url + "/v2/public/channels", params=params, headers=headers
            )
            logging.info(f"Channels successfully fetched from SK API")
            return response.json()
        except Exception as err:
            logging.error(err, exc_info=True)
            return None

    def get_channel_ids(self) -> list[dict]:
        """Fetch all channel IDs from SK API

        Returns:
            list[str]: List of channel IDs
        """

        if not self._bearer:
            self.get_auth_token()

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer { self._bearer }",
        }
        params = {"imageSize": "S", "communityIdentifier": "sk_rs", "languageId": "404"}

        try:
            response = requests.get(
                self.base_url + "/v2/public/channels", params=params, headers=headers
            )
            return [channel["id"] for channel in response.json()]
        except Exception as err:
            logging.error(err, exc_info=True)
            return None

    def get_shows(self) -> dict:
        """Fetch all shows for all SK channels from SK API

        Returns:
            list[dict]: List of shows
        """
        if not self._bearer:
            self.get_auth_token()

        ids = self.get_channel_ids()

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer { self._bearer }",
            "X-UCP-TIME-FORMAT": "timestamp",
        }
        params = {
            "cid": ",".join([str(id) for id in ids]),
            "fromTime": int(pendulum.now().add(days=-7).start_of("day").timestamp()),
            "toTime": int(pendulum.now().add(days=5).end_of("day").timestamp()),
            "communityIdentifier": "sk_rs",
            "languageId": "404",
        }

        try:
            response = requests.get(
                self.base_url + "/v1/public/events/epg", params=params, headers=headers
            )
            logging.info(
                f"{ len(response.json()) } shows successfully fetched from SK API"
            )
            return response.json()
        except Exception as err:
            logging.error(err, exc_info=True)
            return None

    def prepare_channels(self, shows: list[Show]) -> list[Channel]:
        """Prepare channels for saving to database

        Returns:
            list[Show]: List of show embedded documents
        """
        try:
            channels_data = self.get_channels()
            channels = []

            for channel in channels_data:
                matching_shows = [show for show in shows if show.oid == channel["id"]]
                channels.append(self.parser.parse_channel(channel, matching_shows))

            logging.info(f"{len(channels)} channels successfully parsed from SK API")
            return channels
        except Exception as err:
            logging.error(err, exc_info=True)
            return None

    def prepare_shows(self) -> list[Show]:
        """Prepare shows for saving to database.

        Returns:
            list[Show]: List of shows as model objects
        """
        try:
            data = self.get_shows()
            shows = []

            for _, items in data.items():
                for item in items:
                    shows.append(self.parser.parse_show(item))

            logging.info(f"{len(shows)} shows prepared for database.")
            return shows
        except Exception as err:
            logging.error(err, exc_info=True)
            return None

    def scrape(self) -> dict[list]:
        """Scrape SK API and prepare data for saving to database

        Returns:
            dict[list]: Dictionary with lists of channels and shows
        """
        shows = self.prepare_shows()
        channels = self.prepare_channels(shows)

        logging.info(
            f"{len(channels)} channels with {len(shows)} embedded shows scraped."
        )
        return channels
