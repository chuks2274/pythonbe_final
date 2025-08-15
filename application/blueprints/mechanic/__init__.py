from flask import Blueprint # Import Blueprint from Flask to group related routes together

# Create 'mechanic' blueprint to group all mechanic-related routes together
mechanic_bp = Blueprint('mechanic', __name__, url_prefix='/mechanics')  

# Import customer routes after blueprint is defined to avoid circular imports
from . import routes  