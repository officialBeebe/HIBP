import os
import logging
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_DRIVER = os.getenv("DB_DRIVER")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_DATABASE = os.getenv("DB_DATABASE")
    HIBP_API_URL = os.getenv("HIBP_API_URL")
    HIBP_API_KEY = os.getenv("HIBP_API_KEY")
    HIBP_USER_AGENT = os.getenv("HIBP_USER_AGENT")
    SERVICE_URL = os.getenv("SERVICE_URL")
    SERVICE_SECRET_KEY = os.getenv("SERVICE_SECRET_KEY")

    @property
    def db_url(self):
        return f"{self.DB_DRIVER}://{self.DB_USER}:{quote_plus(self.DB_PASSWORD)}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

config = Config()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)