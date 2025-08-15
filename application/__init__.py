from flask import Flask  # Import the Flask class; used to create the main Flask application instance
from .extensions import db, ma, cache, limiter, migrate  # Import Flask extensions: db, ma, cache, limiter, migrate
from .blueprints.mechanic import mechanic_bp  # Import the mechanic blueprint to register mechanic-related routes
from .blueprints.customer import customer_bp # Import the customer blueprint for customer-related routes
from .blueprints.service_ticket import service_ticket_bp # Import the service_ticket blueprint for service ticket routes
from .blueprints.inventory import inventory_bp  # Import the inventory blueprint for inventory/parts routes
from .models import *  # Import all database models (tables) to make them available for ORM and migrations


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