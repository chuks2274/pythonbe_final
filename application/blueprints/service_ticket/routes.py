from flask import request, jsonify # Import `request` to get data from HTTP requests and `jsonify` to send JSON responses
from . import service_ticket_bp # Import the blueprint for service ticket routes from current folder
from application.extensions import db, cache, limiter # Import the database instance, cache, and rate limiter from extensions
from application.models import ServiceTicket, Mechanic, Inventory, Customer # Import models for ServiceTicket, Mechanic, Inventory, and Customer database tables
from .schemas import ticket_schema, tickets_schema # Import schemas to convert ticket objects to and from JSON
from application.utils.auth import token_required # Import decorator to require valid login token
from sqlalchemy.orm import joinedload # Import tool to load related data (mechanics and parts) when querying tickets
from application.error_handlers import handle_db_exceptions # Import decorator to handle database errors gracefully
from ..inventory.schemas import inventories_schema # Import schema for serializing inventory (parts)
from application.utils.role_check import mechanic_required, customer_required # Import role check functions to verify if user is mechanic or customer
from werkzeug.exceptions import NotFound # Import NotFound exception to manually raise 404 errors


# CREATE TICKET (Mechanic Only)
@service_ticket_bp.route('/', methods=['POST'])
@token_required
@limiter.limit("10 per minute")  # Limit access to 10 requests per minute.
@handle_db_exceptions
def create_ticket(current_user_id):
    # Check if current user is a mechanic; if not return error
    _, error = mechanic_required(current_user_id)
    if error:
        return error

    # Get JSON data from request body
    data = request.get_json()

    # Validate that 'vin' is provided
    vin = data.get('vin')
    if not vin:
        return jsonify({"error": "VIN is required."}), 400

    # Check if a service ticket with the same VIN already exists
    existing_ticket = ServiceTicket.query.filter_by(vin=vin).first()
    if existing_ticket:
        # Return error if duplicate VIN found
        return jsonify({"error": "A service ticket with this VIN already exists."}), 400

    # Create new ServiceTicket instance with description, customer_id, and vin from data
    ticket = ServiceTicket(
        description=data['description'],
        customer_id=data['customer_id'],
        vin=vin
    )

    db.session.add(ticket)  # Add new ticket to the database session
    db.session.commit()     # Save the changes to the database

    # Return JSON message with created ticket data, status code 201 (created)
    return jsonify({
        "message": "Service ticket created successfully.",
        "ticket": ticket_schema.dump(ticket)
    }), 201

# GET ALL TICKETS (Mechanic: all tickets; Customer: own tickets with pagination)
@service_ticket_bp.route('/', methods=['GET'])
@token_required
@cache.cached(timeout=30) # Cache this response for 30 seconds to reduce database queries.
@limiter.limit("60 per hour") # Limit access to 60 requests per hour.
@handle_db_exceptions
def get_tickets(current_user_id):
    # Check if current user is a mechanic
    mechanic, mech_error = mechanic_required(current_user_id)
    if mechanic:
        # If mechanic, query all tickets with mechanics and parts loaded
        tickets = ServiceTicket.query.options(
            joinedload(ServiceTicket.mechanics),
            joinedload(ServiceTicket.parts)
        ).all()

        # Return list of all tickets as JSON with HTTP status 200 (OK)
        return jsonify(tickets_schema.dump(tickets)), 200

    # If not mechanic, check if user is a customer
    customer, cust_error = customer_required(current_user_id)
    if customer:
        # Get pagination parameters from query string, defaulting to page 1 and 10 items per page
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Query tickets belonging to the customer with pagination
        paginated = ServiceTicket.query.filter_by(customer_id=customer.id).paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Return paginated tickets with pagination metadata
        return jsonify({
            "message": "Tickets fetched successfully.",
            "tickets": tickets_schema.dump(paginated.items),
            "total": paginated.total,
            "pages": paginated.pages,
            "current_page": paginated.page
        }), 200

    # If user is neither mechanic nor customer, deny access
    return jsonify({"error": "Access denied: Only customers or mechanics can view tickets"}), 403

# GET TICKET BY ID (Mechanic or Customer)
@service_ticket_bp.route('/<int:ticket_id>', methods=['GET'])
@token_required
@cache.cached(timeout=30) # Cache this response for 30 seconds to reduce database queries.
@limiter.limit("60 per hour") # Limit access to 60 requests per hour.
@handle_db_exceptions
def get_ticket_by_id(current_user_id, ticket_id):
    # Query ticket with related mechanics and parts
    ticket = ServiceTicket.query.options(
        joinedload(ServiceTicket.mechanics),
        joinedload(ServiceTicket.parts)
    ).filter_by(id=ticket_id).first()

    # Raise 404 error if ticket not found
    if not ticket:
        raise NotFound(description=f"Service ticket with id {ticket_id} not found.")

    # Check if current user is a mechanic
    mechanic, mech_error = mechanic_required(current_user_id)
    if mechanic:
        # Mechanics can access any ticket
        return jsonify(ticket_schema.dump(ticket)), 200

    # Check if current user is a customer
    customer, cust_error = customer_required(current_user_id)
    if customer:
        # Customers can only access their own tickets
        if ticket.customer_id != customer.id:
            return jsonify({"error": "Access denied: This ticket does not belong to you"}), 403
        return jsonify(ticket_schema.dump(ticket)), 200

    # Deny access if user is neither mechanic nor customer
    return jsonify({"error": "Access denied: Only customers or mechanics can view tickets"}), 403

# UPDATE TICKET BY ID (Mechanic only) 
@service_ticket_bp.route('/<int:ticket_id>', methods=['PUT'])  
@token_required   
@limiter.limit("60 per hour")  # Limit access to 60 requests per hour.
@handle_db_exceptions  
def update_ticket(current_user_id, ticket_id):
    # Check if the current user is a mechanic
    _, error = mechanic_required(current_user_id)
    # Return error response if user is not a mechanic
    if error:
        return error  

    # Get the ticket by ID
    ticket = ServiceTicket.query.get(ticket_id)
    
    # If ticket not found, raise 404 error
    if not ticket:
        raise NotFound(description=f"Service ticket with id {ticket_id} not found.")

    # Get the JSON data from the request body
    data = request.get_json()

    # Update the ticket's description if provided
    if 'description' in data:
        ticket.description = data['description']

    # Commit the changes to the database
    db.session.commit()

    # Return success message with updated ticket data
    return jsonify({
        "message": "Service ticket updated successfully.",
        "ticket": ticket_schema.dump(ticket)
    }), 200

# ASSIGN MECHANIC (Mechanic Only)
@service_ticket_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
@token_required
@limiter.limit("60 per hour") # Limit access to 60 requests per hour.
@handle_db_exceptions
def assign_mechanic(current_user_id, ticket_id, mechanic_id):
    # Check if current user is a mechanic
    _, error = mechanic_required(current_user_id)
    # Return error response if user is not a mechanic
    if error:
        return error

    # Get the ticket by ID
    ticket = ServiceTicket.query.get(ticket_id)
    
    # If ticket not found, raise 404 error
    if not ticket:
        raise NotFound(description=f"Service ticket with id {ticket_id} not found.")

    # Get mechanic by ID
    mech_to_assign = Mechanic.query.get(mechanic_id)
    # If mechanic not found, raise 404 error
    if not mech_to_assign:
        raise NotFound(description=f"Mechanic with id {mechanic_id} not found.")

    # If mechanic is not already assigned to the ticket, assign them
    if mech_to_assign not in ticket.mechanics:
        ticket.mechanics.append(mech_to_assign)

    db.session.commit() # Commit the changes to the database

    # Return success message with updated ticket data
    return jsonify({
        "message": "Mechanic assigned successfully.",
        "ticket": ticket_schema.dump(ticket)
    }), 200

# REMOVE MECHANIC (Mechanic Only)
@service_ticket_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['DELETE'])
@token_required
@limiter.limit("60 per hour") # Limit access to 60 requests per hour.
@handle_db_exceptions
def remove_mechanic(current_user_id, ticket_id, mechanic_id):
    # Check if current user is a mechanic
    _, error = mechanic_required(current_user_id)
    # Return error response if user is not a mechanic
    if error:
        return error

    # Get ticket by ID or raise 404 if not found
    ticket = ServiceTicket.query.get(ticket_id)
    if not ticket:
        raise NotFound(description=f"Service ticket with id {ticket_id} not found.")

    # Get mechanic by ID or raise 404 if not found
    mech_to_remove = Mechanic.query.get(mechanic_id)
    if not mech_to_remove:
        raise NotFound(description=f"Mechanic with id {mechanic_id} not found.")

    # If mechanic is assigned, remove them
    if mech_to_remove in ticket.mechanics:
        ticket.mechanics.remove(mech_to_remove)

    db.session.commit() # Commit the changes to the database

    # Return success message with updated ticket data
    return jsonify({
        "message": "Mechanic removed successfully.",
        "ticket": ticket_schema.dump(ticket)
    }), 200

# EDIT TICKET (Mechanic Only)
@service_ticket_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
@token_required
@limiter.limit("60 per hour") # Limit access to 60 requests per hour.
@handle_db_exceptions
def edit_ticket(current_user_id, ticket_id):
    # Check if current user is a mechanic
    _, error = mechanic_required(current_user_id)
    # Return error response if user is not a mechanic
    if error:
        return error

    # Get ticket by ID
    ticket = ServiceTicket.query.get(ticket_id)
    # Raise 404 if ticket not found
    if not ticket:
        raise NotFound(description=f"Service ticket with id {ticket_id} not found.")

    # Get JSON data from request body
    data = request.get_json()

    # If description provided, update it
    if 'description' in data:
        ticket.description = data['description']

    # If list of mechanics to add is provided, add them if valid and not already assigned
    if 'add_ids' in data:
        for mid in data['add_ids']:
            mech = Mechanic.query.get(mid)
            if mech and mech not in ticket.mechanics:
                ticket.mechanics.append(mech)

    # If list of mechanics to remove is provided, remove them if assigned
    if 'remove_ids' in data:
        for mid in data['remove_ids']:
            mech = Mechanic.query.get(mid)
            if mech and mech in ticket.mechanics:
                ticket.mechanics.remove(mech)

    db.session.commit() # Commit the changes to the database

    # Return updated ticket info with success message
    return jsonify({
        "message": "Ticket updated successfully.",
        "ticket": ticket_schema.dump(ticket)
    }), 200

# DELETE TICKET (Mechanic Only)
@service_ticket_bp.route('/<int:ticket_id>', methods=['DELETE'])
@token_required
@limiter.limit("60 per hour") # Limit access to 60 requests per hour.
@handle_db_exceptions
def delete_ticket(current_user_id, ticket_id):
    # Check if current user is a mechanic
    _, error = mechanic_required(current_user_id)
    # Return error response if user is not a mechanic
    if error:
        return error

    # Get ticket by ID
    ticket = ServiceTicket.query.get(ticket_id)
    # Raise 404 if not found
    if not ticket:
        raise NotFound(description=f"Service ticket with id {ticket_id} not found.")

    db.session.delete(ticket) # Delete ticket from database
    db.session.commit() # Commit the changes to the database

    # Return confirmation message
    return jsonify({"message": f"Service ticket with id {ticket_id} deleted successfully."}), 200

# ADD PARTS (Mechanic Only)
@service_ticket_bp.route('/<int:ticket_id>/add-parts', methods=['POST'])
@token_required
@limiter.limit("60 per minute") # Limit access to 60 requests per hour.
@handle_db_exceptions
def add_parts_to_ticket(current_user_id, ticket_id):
    # Check if current user is a mechanic
    _, error = mechanic_required(current_user_id)
    # Return error response if user is not a mechanic
    if error:
        return error

    # Get ticket by ID
    ticket = ServiceTicket.query.get(ticket_id)
    # Raise 404 if not found
    if not ticket:
        raise NotFound(description=f"Service ticket with id {ticket_id} not found.")

    # Get list of part IDs from JSON body
    part_ids = request.json.get('part_ids', [])

    # Ensure part_ids is a list
    if not isinstance(part_ids, list):
        return jsonify({"error": "part_ids must be a list of integers"}), 400

    # Query parts matching IDs
    parts = Inventory.query.filter(Inventory.id.in_(part_ids)).all()

    # Return error if no valid parts found
    if not parts:
        return jsonify({"error": "No valid parts found for given IDs"}), 404

    # Add parts to ticket if not already added
    for part in parts:
        if part not in ticket.parts:
            ticket.parts.append(part)

    db.session.commit() # Commit the changes to the database

    # Return success message with updated parts list
    return jsonify({
        "message": f"Added {len(parts)} parts to service ticket {ticket_id}",
        "parts": inventories_schema.dump(ticket.parts)
    }), 200

# REMOVE PART (Mechanic Only)
@service_ticket_bp.route('/<int:ticket_id>/remove-part/<int:part_id>', methods=['DELETE'])
@token_required
@limiter.limit("60 per minute") # Limit access to 60 requests per hour.
@handle_db_exceptions
def remove_part_from_ticket(current_user_id, ticket_id, part_id):
    # Check if current user is a mechanic
    _, error = mechanic_required(current_user_id)
    # Return error response if user is not a mechanic
    if error:
        return error

    # Get ticket by ID
    ticket = ServiceTicket.query.get(ticket_id)
    # Raise 404 if not found
    if not ticket:
        raise NotFound(description=f"Service ticket with id {ticket_id} not found.")

    # Get part by ID
    part = Inventory.query.get(part_id)
    # Raise 404 if not found
    if not part:
        raise NotFound(description=f"Part with id {part_id} not found.")

    # If part is linked to the ticket, remove it
    if part in ticket.parts:
        ticket.parts.remove(part)
        db.session.commit() # Commit the changes to the database
        return jsonify({"message": f"Part {part_id} removed from service ticket {ticket_id}"}), 200

    # Return error if part is not associated with this ticket
    return jsonify({"error": "Part not associated with this service ticket"}), 404

# GET PARTS ON TICKET (Customer and Mechanic)
@service_ticket_bp.route('/<int:ticket_id>/parts', methods=['GET'])
@token_required
@limiter.limit("60 per minute")  # Limit access to 60 requests per hour.
@cache.cached(timeout=30) # Cache this response for 30 seconds to reduce database queries.
@handle_db_exceptions
def get_parts_of_ticket(current_user_id, ticket_id):
    # Check if user is a mechanic
    mechanic, mech_error = mechanic_required(current_user_id)
    # Return early if not a mechanic
    if mech_error:
        return mech_error 

    if mechanic:
        # Get ticket by ID
        ticket = ServiceTicket.query.get(ticket_id)
        # Raise 404 if ticket not found
        if not ticket:
            raise NotFound(description=f"Service ticket with id {ticket_id} not found.")
        # Allow mechanic to view parts associated with any service ticket
        return jsonify({
            "message": f"Parts retrieved for service ticket {ticket_id}",
            "parts": inventories_schema.dump(ticket.parts)
        }), 200

    # Check if user is a customer
    customer, cust_error = customer_required(current_user_id)
    # Return early if not a customer
    if cust_error:
        return cust_error  

    if customer:
        # Get ticket by ID
        ticket = ServiceTicket.query.get(ticket_id)
        # Raise 404 if ticket not found
        if not ticket:
            raise NotFound(description=f"Service ticket with id {ticket_id} not found.")

        # Ensure ticket belongs to the logged-in customer
        if ticket.customer_id != customer.id:
            return jsonify({"error": "Unauthorized access"}), 403

        # Return parts for the customer's own ticket
        return jsonify({
            "message": f"Parts retrieved for your service ticket {ticket_id}",
            "parts": inventories_schema.dump(ticket.parts)
        }), 200

    # Deny access if not mechanic or customer
    return jsonify({"error": "Only customers or mechanics can view parts on service tickets"}), 403