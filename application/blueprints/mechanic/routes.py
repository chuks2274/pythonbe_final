from flask import request, jsonify # Import request to get client data and jsonify to send JSON responses.
from . import mechanic_bp # Import the blueprint for mechanic routes.
from application.extensions import db, cache, limiter # Import database session, caching, and rate limiting utilities. 
from application.models import Mechanic # Import the Mechanic model to work with mechanic data.
from .schemas import mechanic_schema, mechanics_schema # Import schemas to format and validate mechanic data (single and multiple).
from application.utils.auth import token_required, encode_token # Import decorators to protect routes and function to create JWT tokens.
from werkzeug.security import generate_password_hash, check_password_hash # Import tools to hash passwords and verify them.
from application.error_handlers import handle_db_exceptions # Import decorator to catch database errors and respond properly.
from sqlalchemy.exc import IntegrityError # Import error type for database integrity violations. 
from sqlalchemy import text # Import function to execute raw SQL queries.
from werkzeug.exceptions import NotFound  # Import NotFound exception to manually raise 404 errors

# CREATE MECHANIC (Public endpoint)
@mechanic_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute")  # Limit to 10 requests per minute to prevent abuse.
@handle_db_exceptions 
def create_mechanic():
    # Parse and get JSON data sent in the request body
    data = request.get_json()  
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    # Check if email already exists
    if Mechanic.query.filter_by(email=data.get('email')).first():
        return jsonify({"error": "Email already registered"}), 400

    # Check if phone already exists
    if Mechanic.query.filter_by(phone=data.get('phone')).first():
        return jsonify({"error": "Phone number already registered"}), 400

    # Hash password if given
    if 'password' in data:
        data['password'] = generate_password_hash(data['password'])
    
    # Create a Mechanic object using the input data.
    mechanic = Mechanic(**data)  

    db.session.add(mechanic) # Add the new mechanic to the database session 
    db.session.commit()  # Save the changes to the database
    
    # Convert mechanic object to a JSON-serializable dictionary.
    response_data = mechanic_schema.dump(mechanic)  
    
    # Remove password from the output for security.
    response_data.pop('password', None)  
    
    # Send back the created mechanic data with HTTP status 201.
    return jsonify(response_data), 201  

# GET ALL MECHANICS (Protected, Cached)
@mechanic_bp.route('/', methods=['GET'])  
@token_required  
@cache.cached(timeout=30)  # Cache this response for 30 seconds to reduce database queries.
@limiter.limit("60 per hour")  # Limit access to 60 requests per hour.
@handle_db_exceptions
def get_mechanics(current_user_id):
    # Extract page number from query parameters; default to page 1.
    page = request.args.get('page', 1, type=int)  
    
    # Extract number of mechanics per page; default to 10.
    per_page = request.args.get('per_page', 10, type=int)  
    
    # Fetch mechanics from the database with pagination.
    paginated = Mechanic.query.paginate(page=page, per_page=per_page, error_out=False)  
    
    # Serialize the list of mechanic objects into JSON-compatible format.
    data = mechanics_schema.dump(paginated.items)  
    
    # Remove password from each mechanic record for security.
    for item in data:
        item.pop('password', None)  
    
    # Return the mechanic data along with pagination details.
    return jsonify({
        "mechanics": data,
        "total": paginated.total,
        "pages": paginated.pages,
        "current_page": paginated.page
    }), 200  

# GET SINGLE MECHANIC BY ID (Protected, Cached)
@mechanic_bp.route('/<int:id>', methods=['GET'])  
@token_required
@cache.cached(timeout=30) # Cache this response for 30 seconds to reduce database queries.
@limiter.limit("60 per hour") # Limit access to 60 requests per hour.
@handle_db_exceptions
def get_mechanic(current_user_id, id):
    # Get mechanic by ID.
    mechanic = Mechanic.query.get(id)  
    
    # Raise 404 error if mechanic doesn't exist.
    if not mechanic:
        raise NotFound(description="Mechanic not found") 
    
    # Convert mechanic object to a JSON-serializable dictionary.
    response_data = mechanic_schema.dump(mechanic)  
    
    # Remove password from the output for security.
    response_data.pop('password', None)  
    
    # Return mechanic data as JSON with HTTP status 200 (OK).
    return jsonify(response_data), 200  

# UPDATE MECHANIC (Protected - only self)
@mechanic_bp.route('/<int:id>', methods=['PUT'])  
@token_required
@limiter.limit("60 per hour") # Limit access to 60 requests per hour.
@handle_db_exceptions
def update_mechanic(current_user_id, id):
    # Check that users can only update their own data; deny access if not.
    if current_user_id != id:
        return jsonify({"error": "Unauthorized access"}), 403  

    # Get mechanic by ID.
    mechanic = Mechanic.query.get(id)
    # Check if mechanic exists; raise 404 error if not found.
    if not mechanic:
        raise NotFound(description=f"Mechanic with id {id} not found.")
    
    # Get the data sent by the user in JSON format.
    data = request.get_json()  
    
    # For each item in the data, if it's the password, hash it for security.
    for key, value in data.items():
        if key == 'password':
            value = generate_password_hash(value)  
        # Update the mechanic's attribute with the new value.
        setattr(mechanic, key, value)  
    db.session.commit()  # Save the changes to the database
    
    # Convert mechanic object to a JSON-serializable dictionary.
    response_data = mechanic_schema.dump(mechanic)  
    
    # Remove password from the output for security.
    response_data.pop('password', None)  
    
    # Return mechanic data as JSON with HTTP status 200 (OK).
    return jsonify(response_data), 200  

# DELETE MECHANIC (Protected - only self)
@mechanic_bp.route('/<int:id>', methods=['DELETE'])  
@token_required
@limiter.limit("60 per hour") # Limit access to 60 requests per hour.
@handle_db_exceptions
def delete_mechanic(current_user_id, id):
    # Check that users can only delete their own account; deny access otherwise.
    if current_user_id != id:
        return jsonify({"error": "Unauthorized: You can only delete your own account"}), 403  
    
    # Get mechanic by ID.
    mechanic = Mechanic.query.get(id)
    # Check if mechanic exists; raise 404 error if not found.
    if not mechanic:
        raise NotFound(description=f"Mechanic with id {id} not found.")

    # Delete mechanic’s associations with service tickets (raw SQL)
    db.session.execute(
        text("DELETE FROM service_mechanic WHERE mechanic_id = :mechanic_id"),
        {"mechanic_id": id}
    )
    db.session.delete(mechanic) # Delete mechanic from the database.  
    db.session.commit()   # Save the changes to the database
    
    # Return success message confirming mechanic deletion with HTTP status 200.
    return jsonify({"message": f"Mechanic with id {id} deleted successfully."}), 200

# GET TOP MECHANICS BY NUMBER OF SERVICE TICKETS (Public, Cached)
@mechanic_bp.route('/top', methods=['GET'])  
@cache.cached(timeout=30)  # Cache this response for 30 seconds to reduce database queries.
@limiter.limit("60 per hour")  # Limit access to 60 requests per hour.
@handle_db_exceptions
def top_mechanics():
    # Get all mechanics from the database.
    mechanics = Mechanic.query.all()  
    
    # Sort mechanics by descending number of service tickets.
    mechanics_sorted = sorted(mechanics, key=lambda m: len(m.service_tickets), reverse=True)  
    
    # Serialize the sorted mechanics list.
    data = mechanics_schema.dump(mechanics_sorted)  
    
    # Remove password from each mechanic for security.
    for item in data:
        item.pop('password', None)  
    
    # Return the list of top mechanics as JSON.
    return jsonify(data), 200  

# MECHANIC LOGIN (Public)
@mechanic_bp.route('/login', methods=['POST'])  
@limiter.limit("10 per minute")  # Limit access to 10 requests per hour.
@handle_db_exceptions
def mechanic_login():
    data = request.get_json()  
    
    # Get mechanic by email.
    mechanic = Mechanic.query.filter_by(email=data['email']).first()  
    
    # Check if password matches.
    if mechanic and check_password_hash(mechanic.password, data['password']):  
        # Create JWT token.
        token = encode_token(mechanic.id)  
        
        # Send back token.
        return jsonify({
        "message": "Login successful",
        "token": token,
        "mechanic_id": mechanic.id,
        "mechanic_name": mechanic.name
    }), 200

    # If login fails, send error message.
    return jsonify({"message": "Invalid credentials"}), 401  