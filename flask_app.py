import os
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from flask import send_file
from application import create_app
from application.extensions import db
from application.error_handlers import register_error_handlers
from application.config import ProductionConfig

# Load environment variable for config
FLASK_ENV = os.getenv("FLASK_ENV", "production")

# Select configuration class
if FLASK_ENV == "development":
    from application.config import Config as SelectedConfig
else:
    SelectedConfig = ProductionConfig

# Create the Flask app
app = create_app(SelectedConfig)

# Enable CORS
CORS(app)

# Register error handlers
register_error_handlers(app)

# Swagger UI setup
SWAGGER_URL = '/docs'
API_URL = '/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Auto Workshop API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Serve Swagger YAML
@app.route('/swagger.yaml')
def swagger_yaml():
    swagger_path = os.path.join(os.path.dirname(__file__), 'static', 'swagger', 'swagger.yaml')
    return send_file(swagger_path, mimetype='text/yaml')

# Create tables if not exist
with app.app_context():
    db.create_all()