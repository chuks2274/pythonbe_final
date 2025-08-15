import unittest # Import Python's built-in unittest framework for writing and running tests
import json # Import JSON module to handle JSON data in requests and responses
from application import create_app # Import Flask app factory to create app instances configured for testing
from application.extensions import db # Import database instance to manage database operations during tests
from application.models import Mechanic # Import Mechanic model to interact with mechanic data in tests

# Setup test environment with app instance, test client, and application context
class MechanicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('config.TestingConfig')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create all database tables
        db.create_all()
# Create a sample Mechanic instance with test data
        mechanic = Mechanic(
            name="Emily Smith",
            email="emily@example.com",
            address="123 Main St",
            phone="555-123-4567",
            specialty="Engine Repair",
            salary=50000.00
        )
# Set the mechanic's password, add the mechanic to the session, and commit to the database
        mechanic.set_password("123456")   
        db.session.add(mechanic)
        db.session.commit()
# Send login request with mechanic's credentials to obtain authentication token
        login_response = self.client.post("/api/mechanics/login", json={
            "email": "emily@example.com",
            "password": "123456"
        })
        print("Login status:", login_response.status_code)
        print("Login response data:", login_response.data.decode())
# Verify that the login request was successful with HTTP status code 200
        self.assertEqual(login_response.status_code, 200)
# Extract JWT token from login response and set Authorization header for authenticated requests
        self.token = json.loads(login_response.data).get("token")
        self.auth_headers = {
            "Authorization": f"Bearer {self.token}"
        }
# Clean up after each test by removing DB session, dropping tables, and popping app context
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
# Test retrieving all mechanics with auth: verify status 200, response structure, and at least one mechanic
    def test_get_all_mechanics(self):
        response = self.client.get("/api/mechanics/", headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        self.assertIn("mechanics", data)
        self.assertIsInstance(data["mechanics"], list)
        self.assertGreaterEqual(len(data["mechanics"]), 1)
# Test creating mechanic with missing required fields returns HTTP 400 Bad Request
    def test_create_mechanic_missing_fields(self):
        response = self.client.post("/api/mechanics/", json={
            "email": "missing@example.com"
        })
        self.assertEqual(response.status_code, 400)
# Test login attempt with incorrect password returns HTTP 401 Unauthorized
    def test_login_with_wrong_password(self):
        response = self.client.post("/api/mechanics/login", json={
            "email": "emily@example.com",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)
# Run the unit tests when the script is executed directly
if __name__ == "__main__":
    unittest.main()