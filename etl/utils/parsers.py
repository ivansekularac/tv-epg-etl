from datetime import datetime

from orm.models import Channel, Show
import pendulum


class MtsParser:
    def __init__(self):
        pass

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
        categories = [c.strip() for c in category_str.split("/")]

        if "Obrazovno" in categories:
            categories.remove("Obrazovno")
            categories.append("Obrazovni")
        elif "Regionalni (Kolažni)" in categories:
            categories.remove("Regionalni (Kolažni)")
            categories.append("Regionalni")

        return categories

    def parse_show(self, item) -> Show:
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
            "poster": item["image"],
            "channel_id": int(item.get("id_channel", "0")),
        }

        return Show(**args)

    def parse_channel(self, item, category) -> Channel:
        """Parsing channel item from API to
        :class:`etl.models.channel.Channel` object.

        Args:
            item (dict): Channel item from API
            category (str): String of categories

        Returns:
            Channel: Parsed Channel object
        """
        args = {
            "channel_id": int(item["id"]),
            "original_id": int(item["id"]),
            "name": item["name"].strip(),
            "logo": item["image"],
            "category": self.parse_categories(category),
        }

        return Channel(**args)


class SkParser:
    def __init__(self) -> None:
        self.image_base_url = "https://images-web.ug-be.cdn.united.cloud"

    def parse_channel(self, item) -> Channel:
        """Parsing channel item from API to
        :class:`etl.models.channel.Channel` object.

        Args:
            item (dict): Channel item from API

        Returns:
            Channel: Parsed Channel object
        """
        args = {
            "channel_id": int("1000" + str(item["id"])),
            "original_id": item["id"],
            "name": item["shortName"].strip(),
            "logo": self.image_base_url + item["images"][0]["path"],
            "category": ["Sportski"],
        }

        return Channel(**args)

    def parse_show(self, channel_id: str, item: dict) -> Show:
        """Parsing show item from API to
        :class:`etl.models.show.Show` object.

        Args:
            channel_id (str): Channel ID
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
            "duration": float((item["startTime"] - item["endTime"]) / 1000 / 60),
            "poster": self.image_base_url + item["images"][1]["path"],
            "channel_id": int("1000" + channel_id),
        }

        return Show(**args)
