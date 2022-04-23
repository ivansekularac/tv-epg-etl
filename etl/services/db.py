import logging

from decouple import config
from mongoengine import connect


class Database:

    _HOST = config("DB_HOST", cast=str)
    _DB = config("DB_NAME", cast=str)
    _USER = config("DB_USER", cast=str)
    _SECRET = config("DB_PSWD", cast=str)

    @staticmethod
    def initialize() -> None:
        """Connect to MongoDB database."""

        try:
            connect(
                host=f"mongodb+srv://{Database._USER}:{Database._SECRET}@{Database._HOST}/{Database._DB}?retryWrites=true&w=majority"
            )
            logging.info("Connected to MongoDB")
        except Exception as err:
            logging.error(err, exc_info=True)

    @staticmethod
    def insert_all(collection, data) -> None:
        """Insert many documents into collection.

        Args:
            collection (MongoDB Document): Collection to insert documents into.
            data (list): List of documents to insert.
        """

        try:
            collection.objects.insert(data)
            logging.info(f"Inserted { len(data) } documents into {collection}")
        except Exception as err:
            logging.error(err, exc_info=True)

        
    @staticmethod
    def drop(collection) -> None:
        """Drop collection.

        Args:
            collection (MongoDB Document): Collection to drop.
        """

        try:
            collection.drop_collection()
            logging.info(f"Dropped { collection }")
        except Exception as err:
            logging.error(err, exc_info=True)