import datetime
import pendulum
import logging
from orm.models import Channel


# function to return all dates between two dates
def daterange(start_date: datetime, end_date: datetime) -> list:
    """Returns a list of dates between two dates

    Args:
        start_date (datetime): start date
        end_date (datetime): end date

    Returns:
        list[datetime]: list of dates between two dates
    """
    dates = []

    for n in range(int((end_date - start_date).days)):
        date = start_date + pendulum.duration(days=n)
        dates.append(date.start_of('day'))
    logging.info(f"{len(dates)} dates generated")
    return dates


def min_max_date(channels: list[Channel]) -> tuple:
    """Returns the min and max dates available in a list of channels

    Args:
        channels (list[Channel]): list of channels

    Returns:
        tuple(datetime, datetime): min and max dates
    """
    dates = []

    for channel in channels:
        for show in channel.shows:
            dates.append(show.start_dt)

    min_date = min(dates)
    max_date = max(dates)

    logging.info(f"Min date is: {min_date} and max date is: {max_date}")
    return (min_date, max_date)
