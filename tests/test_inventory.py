import unittest # Import Python's built-in unittest framework for testing
import json # Import JSON module for handling JSON data in tests
from application import create_app # Import Flask app factory function to create app instances for testing
from application.extensions import db # Import database instance for database operations during tests
from application.models import Mechanic # Import Mechanic model to interact with mechanics data in tests

# Set up test case with app instance, test client, and application context for Inventory tests
class InventoryTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('config.TestingConfig')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
# Create all database tables and add a sample mechanic record for testing
        db.create_all()
        mechanic = Mechanic(
            name="Emily Smith",
            email="emily@example.com",
            address="123 Main St",
            phone="555-123-4567",
            specialty="Engine Repair",
            salary=50000.00
        )
        # Set password for the mechanic, add to session, and commit to save in the database
        mechanic.set_password("123456")
        db.session.add(mechanic)
        db.session.commit()
# Retrieve JWT token for authentication and set the Authorization header
        self.token = self.get_token()
        self.auth_header = {
            "Authorization": f"Bearer {self.token}"
        }
# Clean up the database after each test by removing the session and dropping all tables
    def tearDown(self):
        db.session.remove()
        db.drop_all()
# Properly dispose of the database engine and connection pool, then remove the application context
        engine = db.engine
        engine.dispose()
        if hasattr(engine.pool, "dispose"):
            engine.pool.dispose()

        self.app_context.pop()
# Helper method to log in and retrieve a valid JWT token for authenticated requests
    def get_token(self):
        login_data = {
            "email": "emily@example.com",
            "password": "123456"
        }
        # Send login request, assert successful response, and return the JWT token from response
        response = self.client.post('/api/mechanics/login', json=login_data)
        self.assertEqual(response.status_code, 200)
        return response.get_json()['token']
# Test fetching all inventory items with valid authorization and assert 200 OK response
    def test_get_all_inventory(self):
        response = self.client.get("/api/inventory/", headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
# Test creating an inventory item with a negative price to ensure validation catches invalid input
    def test_post_inventory_negative_price(self):
        data = {
            "name": "Test Negative Price Part",
            "sku": "NEG-PRICE-001",
            "description": "Testing negative price",
            "price": -50.00
        }
        # Send POST request with invalid data and assert that the response returns 400 Bad Request
        response = self.client.post("/api/inventory/", json=data, headers=self.auth_header)
        self.assertEqual(response.status_code, 400)
# Run the unit tests when the script is executed directly
if __name__ == "__main__":
    unittest.main()