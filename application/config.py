import os  # Provides access to environment variables and OS functions

# Base configuration: secret key, database URI, and SQLAlchemy settings
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///db.sqlite3").strip()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Development-specific configuration: enable debug mode
class DevelopmentConfig(Config):
    DEBUG = True

# Testing-specific configuration: enable testing mode and use SQLite test database
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"

# Production-specific configuration: disable debug mode for live deployment
class ProductionConfig(Config):
    DEBUG = False