import logging
from decouple import config
import requests
import pendulum
from utils.parsers import ParserSBB
from orm.models import Channel, Show


class SBB:
    def __init__(self) -> None:
        self.base_url = "https://api-web.ug-be.cdn.united.cloud"
        self.identifiers = [
            ("sk_rs", "404"),
            ("sk_hr", "181"),
            ("sk_si", "386"),
            ("n1_rs", "404"),
            ("n1_hr", "181"),
            ("nova_rs", "404"),
        ]
        self._bearer = self.get_bearer_token()
        self.parser = ParserSBB()

    def get_bearer_token(self):
        """Fetch Bearer token from SK API

        Returns:
            str: Bearer token
        """

        headers = {
            "Accept": "application/json",
            "Authorization": "Basic " + config("SBB_BASIC_TOKEN"),
        }
        params = {"grant_type": "client_credentials"}

        try:
            response = requests.post(
                self.base_url + "/oauth/token", params=params, headers=headers
            )
            logging.info(f"Bearer token successfully fetched from SBB API")

            return response.json()["access_token"]

        except Exception as err:
            logging.error(err, exc_info=True)

    def fetch_epg(self, channels: list[int], community: str, lang: str) -> list[dict]:
        """Fetch shows from API for given channel ids, community and language

        Args:
            channels (list[int]): List of channel ids
            community (str): Community identifier
            lang (str): Language identifier

        Returns:
            list[dict]: List of shows data as dicts
        """
        if not self._bearer:
            logging.error("Bearer token not found")

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer { self._bearer }",
            "X-UCP-TIME-FORMAT": "timestamp",
        }
        params = {
            "cid": ",".join([str(id) for id in channels]),
            "fromTime": int(pendulum.now().add(days=-7).start_of("day").timestamp()),
            "toTime": int(pendulum.now().add(days=5).end_of("day").timestamp()),
            "communityIdentifier": community,
            "languageId": lang,
        }

        try:
            response = requests.get(
                self.base_url + "/v1/public/events/epg", params=params, headers=headers
            )
            # Response is dictionary of channel ids as keys and list of shows as values
            response = response.json()
            shows = []

            for _, s in response.items():
                shows.extend(s)

            logging.info(
                f"{ len(shows) } shows for { community } successfully fetched from API"
            )
            return shows
        except:
            return []

    def fetch_data(self) -> dict[list]:
        """Fetch channels and shows data from API

        Returns:
            dict[list]: Dictionary with channel and show lists
        """

        if not self._bearer:
            logging.error("Bearer token not found")

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer { self._bearer }",
        }

        channels = []
        shows = []

        for identifier in self.identifiers:
            params = {
                "imageSize": "S",
                "communityIdentifier": identifier[0],
                "languageId": identifier[1],
            }

            try:
                response = requests.get(
                    self.base_url + "/v2/public/channels",
                    params=params,
                    headers=headers,
                )
                logging.info(
                    f"{ len(response.json())} channels for {identifier[0]} successfully fetched from API"
                )
                channels.extend(response.json())

                # Fetch shows for these channels
                ids = [channel["id"] for channel in response.json()]
                shows.extend(self.fetch_epg(ids, identifier[0], identifier[1]))

            except Exception as err:
                logging.error(err, exc_info=True)

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
            matching_shows = [show for show in shows if show.oid == item["id"]]
            parsed.append(self.parser.parse_channel(item, matching_shows))
            logging.info(
                f"{item['name']} channel successfully parsed with { len(matching_shows) } shows"
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
