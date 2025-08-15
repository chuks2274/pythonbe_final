import unittest # Import the unittest module, which provides classes and functions to write and run unit tests in Python.
import json # Import the json module to work with JSON data, including parsing and serializing JSON strings.
from werkzeug.security import generate_password_hash # Import generate_password_hash from werkzeug.security to securely hash passwords for storage.
from application import create_app # Import the create_app factory function from the application package to initialize the Flask app for testing.
from application.extensions import db # Import the database instance (SQLAlchemy) from the application's extensions module for database operations in tests.
from application.models import Mechanic, Customer, Inventory, ServiceTicket # Import the ORM model classes Mechanic, Customer, Inventory, and ServiceTicket to create, query, and manipulate data during tests.

# Set up Flask test app, test client, and application context for unit testing.
class ServiceTicketTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config.TestingConfig")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
# Reset the database by dropping all tables and recreating them.
        db.drop_all()
        db.create_all()
# Create a Mechanic instance with sample details for testing purposes.
        self.mechanic = Mechanic(
            name="Emily Smith",
            email="emily@example.com",
            address="123 Main St",
            phone="555-123-4567",
            specialty="Engine Repair",
            salary=50000.00
        )
        # Set hashed password for the mechanic and add the instance to the database session.
        self.mechanic.set_password("123456")
        db.session.add(self.mechanic)
# Create a Customer instance with sample data, hashing the password for security.
        self.customer = Customer(
            name="Ethan Clark",
            email="clark@example.com",
            phone="+1-555-123-4567",
            address="123 Customer Road",
            password=generate_password_hash("custpass")
        )
        # Add the customer instance to the current database session for later commit.
        db.session.add(self.customer)

# Create two sample inventory items (brake pad and oil filter), add them to the database session, and commit the changes.
        self.part1 = Inventory(name="Brake Pad", sku="BP-001", description="Front brake pad", price=25.00)
        self.part2 = Inventory(name="Oil Filter", sku="OF-002", description="Engine oil filter", price=15.00)
        db.session.add_all([self.part1, self.part2])
        db.session.commit()

# Send a POST request to the mechanic login API endpoint with test credentials in JSON format.
        response = self.client.post("/api/mechanics/login", json={
            "email": "emily@example.com",
            "password": "123456"
        })
        # Verify the login request returned HTTP 200, extract the JWT token from the response, and prepare the authorization header for authenticated requests.
        self.assertEqual(response.status_code, 200)
        self.token = json.loads(response.data).get("token")
        self.auth_header = {"Authorization": f"Bearer {self.token}"}
# Clean up after each test by removing the DB session, dropping all tables, disposing of the engine and connection pool, and popping the app context.
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        engine = db.engine
        engine.dispose()
        if hasattr(engine.pool, "dispose"):
            engine.pool.dispose()
        self.app_context.pop()
# Test creating a valid service ticket by sending a POST request with ticket details, linked customer/mechanic IDs, and auth header.
    def test_create_service_ticket(self):
        """Create a valid service ticket"""
        response = self.client.post("/api/service-tickets/", json={
            "description": "Check engine light diagnosis",
            "customer_id": self.customer.id,
            "mechanic_ids": [self.mechanic.id],
            "vin": "1HGCM82633A123456"
        }, headers=self.auth_header)
        # Confirm the ticket creation returned HTTP 201, parse the response JSON, check that a 'ticket' key exists, and verify its description matches the input.
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn("ticket", data)
        self.assertEqual(data["ticket"]["description"], "Check engine light diagnosis")
# Test adding parts by first creating a service ticket, then retrieving its ID from the response for later use.
    def test_add_parts_to_ticket(self):
        """Add parts to an existing service ticket"""
        ticket_response = self.client.post("/api/service-tickets/", json={
            "description": "Brake replacement",
            "customer_id": self.customer.id,
            "mechanic_ids": [self.mechanic.id],
            "vin": "1HGCM82633A123457"
        }, headers=self.auth_header)
        ticket_id = json.loads(ticket_response.data)["ticket"]["id"]
# Send a POST request to add the specified part IDs to the created service ticket, using authentication headers.
        part_response = self.client.post(
            f"/api/service-tickets/{ticket_id}/add-parts",
            json={"part_ids": [self.part1.id, self.part2.id]},
            headers=self.auth_header
        )
        # Verify the add-parts request returned HTTP 200, parse the JSON response, confirm 'parts' key exists, and ensure exactly two parts were added.
        self.assertEqual(part_response.status_code, 200)
        data = json.loads(part_response.data)
        self.assertIn("parts", data)
        self.assertEqual(len(data["parts"]), 2)
# Test updating a service ticket's description by first creating a ticket and extracting its ID from the response.
    def test_update_service_ticket_description(self):
        """Update service ticket description"""
        response = self.client.post("/api/service-tickets/", json={
            "description": "Old description",
            "customer_id": self.customer.id,
            "mechanic_ids": [self.mechanic.id],
            "vin": "1HGCM82633A123458"
        }, headers=self.auth_header)
        ticket_id = json.loads(response.data)["ticket"]["id"]
# Send a PUT request to update the service ticket's description, verify HTTP 200 response, and confirm the description was updated correctly.
        update_response = self.client.put(f"/api/service-tickets/{ticket_id}", json={
            "description": "Updated description"
        }, headers=self.auth_header)
        self.assertEqual(update_response.status_code, 200)
        data = json.loads(update_response.data)
        self.assertEqual(data["ticket"]["description"], "Updated description")
# Test deleting a service ticket by creating one first and retrieving its ID from the response.
    def test_delete_service_ticket(self):
        """Delete service ticket"""
        response = self.client.post("/api/service-tickets/", json={
            "description": "Ticket to delete",
            "customer_id": self.customer.id,
            "mechanic_ids": [self.mechanic.id],
            "vin": "1HGCM82633A123459"
        }, headers=self.auth_header)
        ticket_id = json.loads(response.data)["ticket"]["id"]
# Send a DELETE request to remove the service ticket and verify the response status code is 200 (success).
        delete_response = self.client.delete(f"/api/service-tickets/{ticket_id}", headers=self.auth_header)
        self.assertEqual(delete_response.status_code, 200)
# Attempt to retrieve the deleted service ticket and confirm the response status is 404 (not found).
        get_response = self.client.get(f"/api/service-tickets/{ticket_id}", headers=self.auth_header)
        self.assertEqual(get_response.status_code, 404)

# Run the unit tests when this script is executed directly.
if __name__ == '__main__':
    unittest.main()