from flask import Blueprint # Import Blueprint from Flask to group related routes together

# Create 'inventory' blueprint to group all inventory-related routes together
inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')  

# Import customer routes after blueprint is defined to avoid circular imports
from . import routes  