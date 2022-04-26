from datetime import datetime

from orm.models import Channel, Show, Date
import pendulum


class MtsParser:
    def __init__(self):
        self.default_image = "https://images.unsplash.com/photo-1593784991188-c899ca07263b?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=640&q=50"

    def get_image(self, url) -> str:
        """If there is no image, return default image.

        Args:
            images (str): Url of image

        Returns:
            str: Image URL
        """

        if len(url) == 0:
            return self.default_image

        return url

    def parse_datetime(self, datetime_str) -> tuple:
        """Parse datetime string to datetime object with timezone.
        It handles some edge cases where hours are 24:00 and not 00:00.

        Args:
            datetime_str (str): Datetime string

        Returns:
            tuple: Tuple of datetime object with timezone and unix timestamp
        """
        chars = list(datetime_str)

        if chars[11] == "2" and chars[12] == "4":
            chars[11], chars[12] = "0", "0"

        parsed = pendulum.parse("".join(chars), tz="Europe/Belgrade")

        return (parsed, int(parsed.timestamp()))

    def parse_categories(self, category_str) -> list[str]:
        """Parsing categories string to list of categories.
        Handles potential cases of misspeled categories.

        Args:
            category_str (str): Categories string

        Returns:
            list: List of categories
        """
        try:
            categories = [c.strip() for c in category_str.split("/")]

            if "Obrazovno" in categories:
                categories.remove("Obrazovno")
                categories.append("Obrazovni")
            elif "Regionalni (Kolažni)" in categories:
                categories.remove("Regionalni (Kolažni)")
                categories.append("Regionalni")

            return categories
        except:
            return []

    def parse_show(self, item: dict) -> Show:
        """Parsing show item from API to
        :class:`etl.models.show.Show` object.

        Args:
            item (dict): Show item from API

        Returns:
            Show: Parsed Show object
        """

        args = {
            "title": item["title"],
            "category": item["category"],
            "description": item["description"],
            "start_dt": self.parse_datetime(item["full_start"])[0],
            "end_dt": self.parse_datetime(item["full_end"])[0],
            "start_ts": self.parse_datetime(item["full_start"])[1],
            "end_ts": self.parse_datetime(item["full_end"])[1],
            "duration": float(item["duration"]),
            "poster": self.get_image(item["image"]),
            "oid": int(item.get("id_channel", 0)),
        }

        return Show(**args)

    def parse_channel(self, item: dict, category: str, shows: list[Show]) -> Channel:
        """Parsing channel item from API to
        :class:`etl.models.channel.Channel` object.

        Args:
            item (dict): Channel item from API
            category (str): String of categories
            shows: (list[Show]): List of shows for channel

        Returns:
            Channel: Parsed Channel object
        """
        args = {
            "oid": int(item["id"]),
            "name": item["name"].strip(),
            "logo": item["image"],
            "category": self.parse_categories(category),
            "shows": shows,
        }

        return Channel(**args)


class SkParser:
    def __init__(self) -> None:
        self.image_base_url = "https://images-web.ug-be.cdn.united.cloud"
        self.default_image = "https://images.unsplash.com/photo-1593784991188-c899ca07263b?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=640&q=50"

    def get_image(self, images: list[dict]) -> str:
        """Get image from list of images.
        If there is no image, return default image.

        Args:
            images (list): List of images

        Returns:
            str: Image URL
        """

        if len(images) > 2:
            return self.image_base_url + images[1]["path"]
        elif len(images) > 1:
            return self.image_base_url + images[0]["path"]

        return self.default_image

    def parse_channel(self, item: dict, shows: list[Show]) -> Channel:
        """Parsing channel item from API to
        :class:`etl.models.channel.Channel` object.

        Args:
            item (dict): Channel item from API

        Returns:
            Channel: Parsed Channel object
        """
        args = {
            "oid": item["id"],
            "name": item["shortName"].strip(),
            "logo": self.image_base_url + item["images"][0]["path"],
            "category": ["Sportski"],
            "shows": shows,
        }

        return Channel(**args)

    def parse_show(self, item: dict) -> Show:
        """Parsing show item from API to
        :class:`etl.models.show.Show` object.

        Args:
            item (dict): Show item from API

        Returns:
            Show: Parsed Show object
        """
        args = {
            "title": item["title"],
            "category": "Sport",
            "description": item["shortDescription"],
            "start_dt": pendulum.from_timestamp(
                item["startTime"] / 1000, tz="Europe/Belgrade"
            ),
            "end_dt": pendulum.from_timestamp(
                item["endTime"] / 1000, tz="Europe/Belgrade"
            ),
            "start_ts": item["startTime"] / 1000,
            "end_ts": item["endTime"] / 1000,
            "duration": float((item["endTime"] - item["startTime"]) / 1000 / 60),
            "poster": self.get_image(item["images"]),
            "oid": item["channelId"],
        }

        return Show(**args)


class DateParser:
    @staticmethod
    def parse(date: datetime) -> Date:
        """Parsing datetime object to Date object.

        Args:
            date (datetime): Datetime object

        Returns:
            Date: Parsed Date object
        """
        args = {
            "date_tz": date,
            "timestamp": int(date.timestamp()),
            "weekday": date.format("dddd"),
            "month": date.format("MMMM"),
            "day": int(date.format("D")),
        }
        return Date(**args)
