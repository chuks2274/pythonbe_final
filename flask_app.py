import os
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from flask import send_file, jsonify
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

# === Swagger UI setup (Render-compatible) ===
SWAGGER_URL = '/docs'
API_URL = 'https://pythonbe-final.onrender.com/swagger.yaml'  # Absolute URL for Render

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Auto Workshop API",
        'validatorUrl': None  # Disable online validation to prevent CORS issues
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Serve Swagger YAML
@app.route('/swagger.yaml')
def swagger_yaml():
    swagger_path = os.path.join(os.path.dirname(__file__), 'static', 'swagger', 'swagger.yaml')
    return send_file(swagger_path, mimetype='text/yaml')

# === Add a simple API test route ===
@app.route("/api/")
def api_root():
    return jsonify({"message": "API is working"})

# Create tables if not exist
with app.app_context():
    db.create_all()