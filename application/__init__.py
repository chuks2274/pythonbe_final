from flask import Flask  # Import Flask class to create the Flask application
from .extensions import db, ma, cache, limiter, migrate  # Import extensions
from .blueprints.mechanic import mechanic_bp
from .blueprints.customer import customer_bp
from .blueprints.service_ticket import service_ticket_bp
from .blueprints.inventory import inventory_bp
from .models import *  # Import all models (database tables)


# Function to create and configure the Flask app
def create_app(config_name='config.Config'):
    # Create Flask app instance
    app = Flask(__name__)

    # Load configuration settings from the given config class
    app.config.from_object(config_name)

    # Initialize extensions with the Flask app
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    limiter.init_app(app)

    # Register blueprints with URL prefixes
    app.register_blueprint(mechanic_bp, url_prefix='/api/mechanics')
    app.register_blueprint(customer_bp, url_prefix='/api/customers')
    app.register_blueprint(service_ticket_bp, url_prefix='/api/service-tickets')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')

    # Return the configured Flask app instance
    return app