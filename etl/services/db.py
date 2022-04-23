from mongoengine import connect as mongo_connect
from decouple import config


def connect():
    """Acquire connection to MongoDB"""

    host = config("DB_HOST", cast=str)
    db = config("DB_NAME", cast=str)
    user = config("DB_USER", cast=str)
    secret = config("DB_PSWD", cast=str)

    mongo_connect(
        host=f"mongodb+srv://{user}:{secret}@{host}/{db}?retryWrites=true&w=majority"
    )
