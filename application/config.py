import os

class Config:
    # Base configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
    # Strip whitespace to avoid PostgreSQL errors
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///db.sqlite3").strip()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"

class ProductionConfig(Config):
    DEBUG = False