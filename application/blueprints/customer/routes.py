from flask import request, jsonify # Import request to get data from incoming requests and jsonify to send JSON responses.
from . import customer_bp # Import the customer blueprint so we can add routes to it.
from application.extensions import db, cache, limiter  # Import database object (db), caching system (cache), and rate limiter (limiter).
from application.models import Customer, ServiceTicket # Import the Customer and ServiceTicket models to interact with those tables.
from .schemas import customer_schema, customers_schema, login_schema # Import schemas to validate and format Customer and login data.
from ..service_ticket.schemas import ticket_schema, tickets_schema # Import schemas to format service ticket data. 
from application.utils.auth import encode_token, token_required # Import token functions: one to create a token, the other to protect routes.
from werkzeug.security import generate_password_hash, check_password_hash # Import tools to hash passwords and verify them. 
from application.error_handlers import handle_db_exceptions # Import a decorator that handles and formats database errors.
from werkzeug.exceptions import NotFound  # Import NotFound exception to manually raise 404 errors


# CREATE CUSTOMER (No login needed)
@customer_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute")  # Limit to 10 requests per minute.
@handle_db_exceptions
def create_customer():
    # Get the JSON data sent from the client
    data = request.get_json()

    # Check if any data was provided
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    # If a password is provided, hash it for security
    if 'password' in data:
        data['password'] = generate_password_hash(data['password'])

    # Validate the data using our schema
    errors = customer_schema.validate(data, session=db.session)
    if errors:
        return jsonify(errors), 400

    # Make sure email isn't already used
    if Customer.query.filter_by(email=data.get('email')).first():
        return jsonify({"error": "Email already registered"}), 400

    # Make sure phone number isn't already used
    if Customer.query.filter_by(phone=data.get('phone')).first():
        return jsonify({"error": "Phone number already registered"}), 400

    # Create and save new customer
    new_customer = customer_schema.load(data, session=db.session)
    db.session.add(new_customer)  # Add the new customer to the database
    db.session.commit() # Save the changes to the database

    # Return the new customer data
    return jsonify(customer_schema.dump(new_customer)), 201

# GET ALL CUSTOMERS (Auth required, paginated)
@customer_bp.route('/', methods=['GET'])
@token_required
@cache.cached(timeout=30)  # Cache the response for 30 seconds to reduce load.
@limiter.limit("60 per hour")  # Limit to 60 requests per hour.
@handle_db_exceptions
def get_customers(current_user_id):
    # Get page and per_page from query params with defaults
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)  # Cap at 100

    # Validate page number
    if page < 1:
        return jsonify({"error": "Page number must be greater than 0"}), 400

    # Paginate customer records
    paginated = Customer.query.paginate(page=page, per_page=per_page, error_out=False)

    # Return customer list with pagination details
    return jsonify({
        "customers": customers_schema.dump(paginated.items) or [],
        "total": paginated.total,
        "pages": paginated.pages,
        "current_page": paginated.page
    }), 200

# GET A SINGLE CUSTOMER BY ID
@customer_bp.route('/<int:id>', methods=['GET'])
@token_required
@cache.cached(timeout=30) # Cache the response for 30 seconds to reduce load.
@limiter.limit("60 per hour") # Limit to 60 requests per hour.
@handle_db_exceptions
def get_customer(current_user_id, id):
    # Fetch customer by ID
    customer = Customer.query.get(id)
    
    # Raise 404 if customer does not exist
    if not customer:
        raise NotFound(f"Customer with id {id} not found.")
    
    # Return serialized customer data
    return jsonify(customer_schema.dump(customer)), 200

# UPDATE CUSTOMER BY ID (Only self)
@customer_bp.route('/<int:id>', methods=['PUT'])
@token_required
@limiter.limit("60 per hour")  # Limit to 60 requests per hour.
@handle_db_exceptions
def update_customer(current_user_id, id):
    if current_user_id != id:
        return jsonify({"error": "Unauthorized access"}), 403  
    
    # Get customer by ID or 404 if missing
    customer = Customer.query.get(id)
    if not customer:
        raise NotFound(f"Customer with id {id} not found.")
    
    # Get update data from request.
    data = request.get_json()
    
    # Update each field if it's valid
    for key, value in data.items():
        if hasattr(customer, key):  # If the field exists
            if key == 'password':
                value = generate_password_hash(value)  # Hash new password
            setattr(customer, key, value)  # Set new value

    db.session.commit()  # Save the changes to the database
    
    # Return the updated customer data.
    return jsonify(customer_schema.dump(customer)), 200
    
# DELETE CUSTOMER BY ID (Only self)
@customer_bp.route('/<int:id>', methods=['DELETE'])
@token_required
@limiter.limit("60 per hour")  # Limit to 60 requests per hour.
@handle_db_exceptions
def delete_customer(current_user_id, id):
    if current_user_id != id:
        return jsonify({"error": "Unauthorized access"}), 403  
    
    # Get customer by ID or 404 if missing
    customer = Customer.query.get(id)
    if not customer:
        raise NotFound(f"Customer with id {id} not found.")
    
    db.session.delete(customer)  # Remove the customer from the database session 
    db.session.commit()  # Save the changes to the database
    
    # Send success message confirming customer deletion
    return jsonify({"message": f"Customer with id {id} deleted successfully."}), 200

# LOGIN - Get Token (Public)
@customer_bp.route('/login', methods=['POST'])  
@limiter.limit("10 per minute")  # Limit to 10 requests per minute. 
@handle_db_exceptions
def login():
    # Get login credentials.
    data = request.get_json()  
    errors = login_schema.validate(data)
    if errors:
        return jsonify(errors), 400  

    # Look for the user by email
    customer = Customer.query.filter_by(email=data['email']).first()

    # If user exists and password matches
    if customer and check_password_hash(customer.password, data['password']):
        token = encode_token(customer.id)  # Create JWT
        return jsonify({
        "message": "Login successful",
        "token": token,
        "customer_id": customer.id,
        "customer_name": customer.name
    }), 200

    return jsonify({"message": "Invalid credentials"}), 401  
    # If login fails, return unauthorized.

# GET LOGGED-IN CUSTOMER'S SERVICE TICKETS
@customer_bp.route('/my-tickets', methods=['GET']) 
@token_required  
@limiter.limit("60 per hour")  # Limit to 60 requests per hour. 
@handle_db_exceptions
def get_customer_tickets(current_user_id):
    
    # Check if user wants only IDs (summary) or full customer data
    summary = request.args.get('summary', 'false').lower() == 'true'  
    # Get all tickets for the logged-in customer.
    tickets = ServiceTicket.query.filter_by(customer_id=current_user_id).all() 

    # If summary=true, return just the ticket IDs.
    if summary:
        return jsonify([t.id for t in tickets]), 200  
    
    # Otherwise, return all the full ticket details.
    return jsonify(tickets_schema.dump(tickets)), 200  