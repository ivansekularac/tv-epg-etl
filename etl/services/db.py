from mongoengine import connect
from decouple import config
import logging


class Database:

    _HOST = config("DB_HOST", cast=str)
    _DB = config("DB_NAME", cast=str)
    _USER = config("DB_USER", cast=str)
    _SECRET = config("DB_PSWD", cast=str)

    @staticmethod
    def initialize():
        """Connect to MongoDB database."""

        try:
            connect(
                host=f"mongodb+srv://{Database._USER}:{Database._SECRET}@{Database._HOST}/{Database._DB}?retryWrites=true&w=majority"
            )
            logging.info("Connected to MongoDB")
        except Exception as err:
            logging.error(err, exc_info=True)
