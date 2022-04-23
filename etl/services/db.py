from mongoengine import connect as mongo_connect
from decouple import config
import logging


def connect():
    """Acquire connection to MongoDB"""

    host = config("DB_HOST", cast=str)
    db = config("DB_NAME", cast=str)
    user = config("DB_USER", cast=str)
    secret = config("DB_PSWD", cast=str)

    try:
        mongo_connect(
            host=f"mongodb+srv://{user}:{secret}@{host}/{db}?retryWrites=true&w=majority"
        )
        logging.info("Connected to MongoDB")
    except Exception as err:
        logging.error(err, exc_info=True)
        return None


    
