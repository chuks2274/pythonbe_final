from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy to manage database operations
from flask_marshmallow import Marshmallow # Import Marshmallow to help with converting data to/from JSON
from flask_caching import Cache # Import Cache to speed up responses by storing results temporarily
from flask_limiter import Limiter # Import Limiter to limit how many requests a user can make (rate limiting)
from flask_limiter.util import get_remote_address # Import function to get user's IP address for rate limiting
from flask_migrate import Migrate # Import Migrate to help with database schema changes (migrations)


# Create SQLAlchemy instance for database management
db = SQLAlchemy()

# Create Marshmallow instance for serialization/deserialization
ma = Marshmallow()

# Create Cache instance, using a simple in-memory cache
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

# Create Limiter instance, limiting users to 100 requests per hour by their IP address
limiter = Limiter(key_func=get_remote_address, default_limits=["100 per hour"])

# Create Migrate instance to handle database migrations (changing tables, columns, etc.)
migrate = Migrate()