from datetime import datetime

from orm.models import Channel, Show
from pytz import timezone


class MtsParser:
    def __init__(self):
        pass

    def parse_datetime(self, datetime_str) -> datetime:
        """Parse datetime string to datetime object with timezone.
        It handles some edge cases where hours are 24:00 and not 00:00.

        Args:
            datetime_str (str): Datetime string

        Returns:
            datetime: Parsed datetime object with timezone
        """
        chars = list(datetime_str)

        if chars[11] == "2" and chars[12] == "4":
            chars[11], chars[12] = "0", "0"

        without_tz = datetime.strptime("".join(chars), "%Y-%m-%d %H:%M:%S")
        return timezone("Europe/Belgrade").localize(without_tz)

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
            "start": self.parse_datetime(item["full_start"]),
            "end": self.parse_datetime(item["full_end"]),
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
            "name": item["name"].strip(),
            "logo": item["image"],
            "category": self.parse_categories(category),
        }

        return Channel(**args)
