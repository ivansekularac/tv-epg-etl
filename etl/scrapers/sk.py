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

    def get_shows(self, channel_ids: list[int]) -> dict:
        """Fetch all shows for all SK channels from SK API

        Args:
            channel_ids (list[int]): List of Channel IDs

        Returns:
            list[dict]: List of shows
        """
        if not self._bearer:
            self.get_auth_token()

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer { self._bearer }",
            "X-UCP-TIME-FORMAT": "timestamp",
        }
        params = {
            "cid": ",".join([str(id) for id in channel_ids]),
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

    def prepare_channels(self) -> list[Channel]:
        """Prepare channels for saving to database

        Returns:
            list[Channel]: List of channel documents to be saved to database
        """
        try:
            channels = self.get_channels()
            sk = [self.parser.parse_channel(channel) for channel in channels]
            logging.info(f"{len(sk)} channels successfully parsed from SK API")
            return sk
        except Exception as err:
            logging.error(err, exc_info=True)
            return None

    def prepare_shows(self, channel_ids: list[int]) -> list[Show]:
        """Prepare shows for saving to database.

        Returns:
            list[Show]: List of shows as model objects
        """
        try:
            data = self.get_shows(channel_ids)
            shows = []

            for id, events in data.items():
                for event in events:
                    shows.append(self.parser.parse_show(id, event))

            logging.info(f"{len(shows)} shows prepared for database.")
            return shows
        except Exception as err:
            print(err)
            logging.error(err, exc_info=True)
            return None
