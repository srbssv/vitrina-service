import os
from sanic.config import Config


class VitrinaConfig(Config):
    DATABASE_URL = os.environ["DATABASE_URL"]
    REDIS_URL = os.environ["REDIS_URL"]
    DEBUG = os.environ["DEBUG"]
    PROVIDER_TIMEOUT = 30
    REDIS_KEY_EXPIRE = 1200
