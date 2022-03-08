import os
from sanic.config import Config


class VitrinaConfig(Config):
    DATABASE_URL = os.environ["DATABASE_URL"]
    REDIS_URL = os.environ["REDIS_URL"]
