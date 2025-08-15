from flask import Blueprint # Import Blueprint from Flask to group related routes together

# Create 'service_ticket' blueprint to group all service_ticket-related routes together
service_ticket_bp = Blueprint('service_ticket', __name__, url_prefix='/service-tickets')  

# Import customer routes after blueprint is defined to avoid circular imports
from . import routes  