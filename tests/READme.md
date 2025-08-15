# Mechanic Workshop API Test

![CI/CD Pipeline](https://github.com/chuks2274/pythonbe_final/actions/workflows/main.yaml/badge.svg)

## CI/CD Pipeline

This project uses **GitHub Actions** for continuous integration and deployment to **Render**.

### Workflow Overview
- **Build:** Installs dependencies.
- **Test:** Runs automated tests.
- **Deploy:** Automatically deploys to Render if tests pass and changes are pushed to `main`.

### Live Deployment

- **API Documentation (Swagger UI):** https://pythonbe-final.onrender.com/docs  
- **Base API URL:** https://pythonbe-final.onrender.com/api/

## test_customers.py
### What This File Does
This test file uses Python’s built-in unittest framework to validate the Customers endpoint of a Flask-based API. It ensures the correct behavior of key routes, including customer listing and validation for customer creation.
The test suite uses a JWT-based authentication flow and simulates authorized requests against protected API endpoints.

Features Covered
Authentication Setup
Logs in using a test customer account (clark@example.com) via /api/customers/login.
Retrieves a JWT token from the login response.
Includes the token in the Authorization header for all protected requests.

## test_inventory.py
### What This File Does
This test file uses Python’s built-in unittest framework to validate the Inventory endpoint of a Flask-based API. It ensures the Inventory-related routes function correctly, particularly in the areas of authentication, input validation, and isolated test database setup.

Features Covered
Authentication Setup
Creates a test mechanic in the database.
Logs in via /api/mechanics/login to retrieve a JWT token.
Uses the token to authorize requests to protected endpoints.

## test_mechanics.py
### What This File Does
This test file uses Python’s built-in unittest framework to validate the Mechanics endpoint of a Flask-based API. It ensures the mechanics-related routes work correctly, including authentication, input validation, and proper response handling.
The file is part of a test suite for the Mechanic Workshop API and includes setup and teardown for an isolated test database environment using SQLAlchemy.

Features Covered
Authentication Setup
A test mechanic (Emily Smith) is created in the test database.
The test logs in via /api/mechanics/login to retrieve a valid JWT token.
Authenticated routes include the token in the Authorization header.

## test_service_tickets.py
### What This File Does
This test file uses Python’s built-in unittest framework to validate the Service Tickets endpoint of a Flask-based API. It ensures the correct functionality of key routes for creating, updating, deleting, and managing service tickets and their associated parts.
It uses an isolated test database to create and manipulate real test data, allowing for safe, repeatable test runs without affecting production data.

Features Covered
Authentication Setup
A test mechanic (Emily Smith) is created with a hashed password.
The test logs in via /api/mechanics/login to obtain a valid JWT token.
Authenticated requests include the token in the Authorization header.

## How to Run the Tests
To run the tests from the command line, navigate to your project root and execute:

# Run Mechanics tests
python -m unittest tests.test_mechanics

# Run Customers tests
python -m unittest tests.test_customers

# Run Inventory tests
python -m unittest tests.test_inventory

# Run Service Tickets tests
python -m unittest tests.test_service_tickets

## Or run all tests at once:

python -m unittest discover tests