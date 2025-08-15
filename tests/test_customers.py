import unittest # Import Python's built-in unit testing framework
from flask_app import app # Import the Flask application instance from the app module

# Test case setup initializing test client and authentication token for Customers API tests
class CustomersTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.token = self.get_token()
        self.auth_header = {
            "Authorization": f"Bearer {self.token}"
        }
# Prepare login credentials to obtain an authentication token
    def get_token(self):
        login_data = {
            "email": "clark@example.com",   
            "password": "123456"
        }
        # Send login request, verify success, and extract JWT token from response
        response = self.client.post('/api/customers/login', json=login_data)
        print(response.status_code, response.data)   
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        return json_data['token']  
# Test retrieving all customers with valid authentication returns status 200
    def test_get_all_customers(self):
        response = self.client.get("/api/customers/", headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
# Test creating a customer with missing required fields returns status 400 (Bad Request)
    def test_post_customer_missing_fields(self):
        data = {"first_name": "Jane"}   
        response = self.client.post("/api/customers/", json=data, headers=self.auth_header)
        self.assertEqual(response.status_code, 400)
# Run all unittest test cases when this script is executed directly
if __name__ == "__main__":
    unittest.main()