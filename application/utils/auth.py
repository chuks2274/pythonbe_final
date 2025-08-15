import os # Import operating system module to access environment variables
import jwt # Import jwt library to encode and decode JSON Web Tokens
from datetime import datetime, timedelta # Import datetime classes to handle token expiration times
from functools import wraps # Import wraps decorator to preserve function metadata when creating decorators
from flask import request, jsonify # Import request and jsonify from Flask to get HTTP request data and send JSON responses


# Get the secret key from environment variables; use 'supersecret' if not set
SECRET_KEY = os.getenv('SECRET_KEY', 'supersecret')


# Function to create a JWT token for a given user ID
def encode_token(user_id):
    # Prepare data to include in the token
    payload = {
        'user_id': user_id,                            # Save the user's ID
        'exp': datetime.utcnow() + timedelta(hours=1) # Set expiration to 1 hour from now
    }
    # Encode the payload into a JWT string using the secret key and HS256 algorithm
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


# Decorator to require a valid JWT token for protected routes
def token_required(f):
    @wraps(f)  # Keep the original function's metadata intact
    def decorated(*args, **kwargs):
        token = None

        # Check if the request has an Authorization header with a Bearer token
        if 'Authorization' in request.headers:
            # Extract token from header, format is usually "Bearer <token>"
            token = request.headers['Authorization'].split(" ")[1]

        # If token not found in header, return error message and 401 Unauthorized
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            # Decode token to get the payload using the secret key
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # Extract user_id from token payload
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            # Token has expired; return error message and 401 status
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            # Token is invalid or malformed; return error message and 401 status
            return jsonify({'message': 'Invalid token'}), 401

        # Call the original function, passing the current_user_id as the first argument
        return f(current_user_id, *args, **kwargs)

    # Return the decorated version of the function
    return decorated