from functools import wraps # Import wraps to create decorators that keep the original function's info
from flask import jsonify # Import jsonify to send JSON responses
from sqlalchemy.exc import SQLAlchemyError, IntegrityError # Import SQLAlchemy exceptions for database errors
from werkzeug.exceptions import NotFound # Import NotFound exception for 404 errors
from application.extensions import db # Import database instance to rollback transactions if errors happen
import traceback # Import traceback to print detailed error stack traces (useful for debugging)


# Decorator to catch and handle database-related errors in route functions
def handle_db_exceptions(fn):
    @wraps(fn)  # Preserve the original function's metadata
    def wrapper(*args, **kwargs):
        try:
            # Try to run the original function
            return fn(*args, **kwargs)
        except IntegrityError as e:
            # Handle database integrity errors (like duplicate keys)
            db.session.rollback()  # Undo current DB changes to keep data safe
            return jsonify({"error": "Integrity error", "details": str(e)}), 400  # Send error with HTTP 400 Bad Request
        except NotFound as e:
            # Handle 404 errors when something is not found
            return jsonify({"error": "Not Found", "details": str(e)}), 404
        except SQLAlchemyError as e:
            # Handle general SQLAlchemy database errors
            db.session.rollback()  # Undo DB changes to avoid corrupt data
            return jsonify({"error": "Database error", "details": str(e)}), 500  # Internal Server Error
        except Exception as e:
            # Catch any other unexpected errors
            db.session.rollback()  # Undo DB changes as a precaution
            print(traceback.format_exc())  # Print detailed error trace to the console for debugging
            return jsonify({"error": "Unexpected error", "details": str(e)}), 500  # Internal Server Error
    return wrapper


# Function to add global error handlers to the Flask app
def register_error_handlers(app):
    # Handle 404 Not Found error globally
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            "error": "Not Found",
            "message": "The requested URL was not found. Please check the path or spelling."
        }), 404

    # Handle 405 Method Not Allowed error globally
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "error": "Method Not Allowed",
            "message": "The method is not allowed for the requested URL. Check the API documentation."
        }), 405

    # Handle 500 Internal Server Error globally
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later."
        }), 500

    # Handle any other unexpected exceptions globally
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        return jsonify({
            "error": "Unexpected Error",
            "message": str(error)
        }), 500