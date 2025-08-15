from flask import request, jsonify # Import request to get data from client, jsonify to send JSON responses.
from werkzeug.exceptions import NotFound # Import error to handle "not found" cases (used later).
from . import inventory_bp # Import the blueprint for inventory routes.
from application.extensions import db, cache, limiter # Import database session, caching system, and rate limiter. 
from application.models import Inventory # Import Inventory model to work with parts data.
from .schemas import inventory_schema, inventories_schema # Import schemas to validate and format single/multiple parts.
from application.utils.auth import token_required # Import decorator to protect routes (require login).
from application.utils.role_check import mechanic_required # Import function to check if user is a mechanic (role-based access). 
from application.error_handlers import handle_db_exceptions # Import decorator to catch and format database errors nicely.


# CREATE PART – Only mechanics can create parts
@inventory_bp.route('/', methods=['POST'])  
@token_required  
@limiter.limit("10 per minute")  # Limit to 10 requests per minute. 
@handle_db_exceptions  
def create_part(current_user_id):
    # Check if current user is a mechanic; get mechanic object and any error response
    mechanic, error_response = mechanic_required(current_user_id)  
    
    # If not a mechanic, return an error response.
    if error_response:
        return error_response  
    
    # Get new part data sent by the user in the request body
    data = request.get_json()  
    
    # Check if a part with the same name already exists.
    existing_part = Inventory.query.filter_by(name=data.get('name')).first()  

    if existing_part:
        return jsonify({"error": "Duplicate part with the same name exists"}), 400  
    
    # Validate that price is present and not negative
    if 'price' not in data or data['price'] < 0:
        return jsonify({'error': 'Price must be zero or positive'}), 400
    
    # Convert input data into an Inventory object.
    part = inventory_schema.load(data)  

    db.session.add(part)  # Add new part to the database.
    db.session.commit()  # Save the changes to the database

    # Return success message and the new part data.
    return jsonify({
        "message": "Part created successfully",
        "part": inventory_schema.dump(part)
    }), 201


# GET ALL PARTS – Only mechanics, with pagination
@inventory_bp.route('/', methods=['GET'])  
@token_required  
@limiter.limit("60 per hour")  # Limit to 60 requests per minute. 
@cache.cached(timeout=30)  # Cache the response for 30 seconds to reduce load.
@handle_db_exceptions
def get_parts(current_user_id):
    # Check if current user is a mechanic; get mechanic object and any error response
    mechanic, error_response = mechanic_required(current_user_id)  
    
# If not a mechanic, return an error response.
    if error_response:
        return error_response  
        
# Get page number from query (default 1).
    page = request.args.get('page', 1, type=int) 

    # Get items per page (default 10).
    per_page = request.args.get('per_page', 10, type=int)

# Get parts with pagination.
    paginated = Inventory.query.paginate(page=page, per_page=per_page, error_out=False)  

# Return parts list and paging info.
    return jsonify({
        "message": "Parts retrieved successfully",
        "parts": inventories_schema.dump(paginated.items),
        "total": paginated.total,
        "pages": paginated.pages,
        "current_page": paginated.page
    }), 200  

# GET SINGLE PART BY ID – Only mechanics
@inventory_bp.route('/<int:id>', methods=['GET'])  
@token_required  
@limiter.limit("60 per hour")  # Limit to 60 requests per minute. 
@cache.cached(timeout=30)  # Cache the response for 2 minutes to reduce load.
@handle_db_exceptions
def get_part(current_user_id, id):
    # Check if current user is a mechanic; get mechanic object and any error response
    mechanic, error_response = mechanic_required(current_user_id)  
    
    # If not a mechanic, return an error response.
    if error_response:
        return error_response

    # Get the Inventory item by ID
    part = Inventory.query.get(id)
    # Raise 404 error if part not found
    if not part:
        raise NotFound(description=f"Part with id {id} not found.")

    # Return success message and part data as JSON (status 200)
    return jsonify({
        "message": "Part retrieved successfully",
        "part": inventory_schema.dump(part)
    }), 200 

# UPDATE PART BY ID – Only mechanics
@inventory_bp.route('/<int:id>', methods=['PUT'])  
@token_required  
@limiter.limit("60 per hour")  # Limit to 60 requests per minute. 
@handle_db_exceptions
def update_part(current_user_id, id):
    # Check if current user is a mechanic; get mechanic object and any error response
    mechanic, error_response = mechanic_required(current_user_id)  
    
    # If not a mechanic, return an error response.
    if error_response:
        return error_response

    # Get the Inventory item by ID
    part = Inventory.query.get(id)  
    # Raise 404 error if part not found
    if not part:
        raise NotFound(description=f"Part with id {id} not found.")
    
    # Get new part data sent by the user in the request body
    data = request.get_json()  

    if 'name' in data:
        # Check if new name is already taken by another part.
        existing_part = Inventory.query.filter(Inventory.name == data['name'], Inventory.id != id).first()
        if existing_part:
            return jsonify({"error": "Another part with the same name exists"}), 400

    # Update each field with new data.
    for key, value in data.items():
        setattr(part, key, value)  
        
    db.session.commit() # Save the changes to the database

    # Return success message and updated part data as JSON with status 200
    return jsonify({
        "message": "Part updated successfully",
        "part": inventory_schema.dump(part)
    }), 200 
    
# DELETE PART BY ID – Only mechanics
@inventory_bp.route('/<int:id>', methods=['DELETE'])  
@token_required  
@limiter.limit("60 per hour") # Limit to 60 requests per minute.
@handle_db_exceptions
def delete_part(current_user_id, id):
    # Check if current user is a mechanic; get mechanic object and any error response
    mechanic, error_response = mechanic_required(current_user_id) 

    # If not a mechanic, return an error response.
    if error_response:
        return error_response

    # Get the Inventory item by ID
    part = Inventory.query.get(id)  
    # Raise 404 error if part not found
    if not part:
        raise NotFound(description=f"Part with id {id} not found.")

    db.session.delete(part)   # Remove the part from the database session 
    db.session.commit()  # Save the changes to the database

    # Return success message confirming deletion of part with given ID (status 200)
    return jsonify({"message": f"Part with id {id} deleted successfully."}), 200