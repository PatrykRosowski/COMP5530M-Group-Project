import os
from dotenv import load_dotenv

load_dotenv()

WTF_CSRF_ENABLE = True

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DATA_FOLDER = os.path.join(BASE_DIR, "app", "algorithm_engine")

    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {"dev": DevelopmentConfig, "prod": ProductionConfig, "default": DevelopmentConfig}
