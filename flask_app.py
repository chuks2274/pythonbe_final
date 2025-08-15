import os   # Import OS module for environment variables and file system operations
from flask_cors import CORS  # Import CORS to enable cross-origin requests for the Flask app
from flask_swagger_ui import get_swaggerui_blueprint # Import helper to serve Swagger UI for API docs
from flask import send_file, jsonify  # Import Flask utilities to send files and return JSON responses
from application import create_app # Import factory function to create the Flask app instance
from application.extensions import db # Import SQLAlchemy instance for database operations
from application.error_handlers import register_error_handlers # Import function to register error handlers
from application.config import ProductionConfig  # Import the production configuration class

# Load environment variable for Flask environment, default to "production"
FLASK_ENV = os.getenv("FLASK_ENV", "production")

# Select configuration based on environment: use development config if FLASK_ENV is "development", otherwise use production config
if FLASK_ENV == "development":
    from application.config import Config as SelectedConfig
else:
    SelectedConfig = ProductionConfig

# Create the Flask application instance with the selected configuration
app = create_app(SelectedConfig)

# Enable Cross-Origin Resource Sharing (CORS) for the Flask app
CORS(app)

# Register error handlers
register_error_handlers(app)

# Setup Swagger UI for Render deployment
SWAGGER_URL = '/docs'
API_URL = 'https://pythonbe-final.onrender.com/swagger.yaml'  

# Create Swagger UI blueprint with custom app name and disable online validator
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Auto Workshop API",
        'validatorUrl': None  
    }
)
# Register the Swagger UI blueprint at the /docs URL prefix
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Serve the Swagger YAML file for Swagger UI
@app.route('/swagger.yaml')
def swagger_yaml():
    swagger_path = os.path.join(os.path.dirname(__file__), 'static', 'swagger', 'swagger.yaml')
    return send_file(swagger_path, mimetype='text/yaml')

# Add a simple API test route
@app.route("/api/")
def api_root():
    return jsonify({"message": "API is working"})

# Create tables if they do not exist
with app.app_context():
    db.create_all()