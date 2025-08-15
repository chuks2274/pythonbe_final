from flask import jsonify # Import jsonify to send JSON responses
from application.models import Mechanic, Customer # Import Mechanic and Customer models from your application


# Function to check if the current user is a mechanic
def mechanic_required(current_user_id):
    # Try to get a Mechanic object with the current user's ID from the database
    mechanic = Mechanic.query.get(current_user_id)

    # If no mechanic found, return None and an error response with status 403 (forbidden)
    if not mechanic:
        return None, (jsonify({"error": "Only mechanics can perform this action"}), 403)

    # If mechanic found, return the mechanic object and no error
    return mechanic, None


# Function to check if the current user is a customer
def customer_required(current_user_id):
    # Try to get a Customer object with the current user's ID from the database
    customer = Customer.query.get(current_user_id)

    # If no customer found, return None and an error response with status 403 (forbidden)
    if not customer:
        return None, (jsonify({"error": "Only customers can perform this action"}), 403)

    # If customer found, return the customer object and no error
    return customer, None