from flask import Blueprint # Import Blueprint from Flask to group related routes together

# Create 'customer' blueprint to group all customer-related routes together
customer_bp = Blueprint('customer', __name__)  

# Import customer routes after blueprint is defined to avoid circular imports
from . import routes  