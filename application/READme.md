# Mechanic Workshop API

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

## app.py
### What This File Does
This file is responsible for **starting the Flask application** and **initializing the database tables** when the application is run. It uses the `create_app` function (following the Flask application factory pattern) and SQLAlchemy for database management.
When executed directly, this file:
**Creates the Flask application** using `create_app()`.
**Pushes the application context**, allowing database operations to be performed.
**Initializes all database tables** defined in the application's models.
**Starts the Flask development server** with debugging enabled.

## config.py
### What This File Does
This file defines the **configuration settings** for the Flask application, including database connections, caching, and security keys.

### Loads Environment Variables 
Reads values from a `.env` file to configure sensitive settings like the database URL and secret keys.

### Defines the Config Class
Holds all configuration options for the Flask application in a single class (`Config`).

### Database Configuration  
Uses `SQLALCHEMY_DATABASE_URI` to specify the database connection string.
Disables `SQLALCHEMY_TRACK_MODIFICATIONS` to save memory and avoid unnecessary overhead.

### Security Key
Sets a `SECRET_KEY` used by Flask for securely signing sessions and other cryptographic operations.
If not provided in the environment, a default key (`supersecret`) is used.

### Caching Configuration 
Sets `CACHE_TYPE` to `"SimpleCache"` to enable in-memory caching for improved performance.

## models.py
### What This File Does
This file defines the **database models** and **association tables** for managing customers, mechanics, service tickets, and inventory in the application. It uses SQLAlchemy ORM to map Python classes to database tables.

### Association Tables

`service_mechanic` 
A many-to-many relationship between service tickets and mechanics.  
Allows multiple mechanics to be assigned to a single service ticket.

`service_inventory` 
A many-to-many relationship between service tickets and inventory items.  
Allows multiple inventory parts to be linked to a single service ticket.

### Models

`Customer`
Represents a customer in the system.  
Key attributes include `name`, `email`, `phone`, `address`, and `password`.  
Has a **one-to-many** relationship with `ServiceTicket` (a customer can have multiple service tickets).

`Mechanic`
Represents a mechanic with attributes such as `name`, `specialty`, `email`, `phone`, `address`, and `salary`.  
Has a **many-to-many** relationship with `ServiceTicket` through the `service_mechanic` table.

`ServiceTicket`
Represents a service request or repair job.  
Attributes include `description` and `customer_id`.  
Linked to **customers**, **mechanics**, and **inventory parts** via relationships:
Many-to-one with `Customer`.
Many-to-many with `Mechanic`.
Many-to-many with `Inventory`.

`Inventory`
Represents items or parts available for use in repairs.  
Attributes include `name`, `sku`, `description`, and `price`.  
Has a **many-to-many** relationship with `ServiceTicket` through the `service_inventory` table.

## extensions.py
### What This File Does
This file is responsible for **initializing the core Flask extensions** used throughout the application. These extensions provide database management, serialization, caching, request limiting, and database migrations.

### Database Management (`db`) 
Sets up SQLAlchemy, the Object Relational Mapper (ORM), for interacting with the database using Python classes and objects.

### Serialization (`ma`)  
Initializes Marshmallow, which handles object serialization and deserialization (e.g., converting Python objects to JSON and vice versa).

### Caching (`cache`)  
Configures a simple in-memory cache (`SimpleCache`) to improve performance by temporarily storing frequently accessed data.

### Rate Limiting (`limiter`) 
Sets up request rate limiting using client IP addresses as identifiers.
By default, limits each client to **100 requests per hour** to prevent abuse.

### Database Migrations (`migrate`)  
Enables database schema migrations using Flask-Migrate, which is built on top of Alembic.
Allows smooth database schema updates without losing existing data.

## __init__.py
### What This File Does
This file defines the **Flask application factory** function, `create_app()`, which is responsible for creating and configuring the Flask app instance. It sets up extensions, configuration, and routes (blueprints).

### Create the Flask Application
A new Flask app instance is created when `create_app()` is called.
Configuration settings are loaded from the `Config` class.

### Initialize Extensions
**Database (SQLAlchemy):** Enables ORM-based database interactions.
**Serialization (Marshmallow):** Handles data serialization and validation.
**Migrations (Flask-Migrate):** Manages database schema changes without losing data.
**Caching:** Sets up application-level caching for performance optimization.
**Rate Limiting:** Controls the rate of incoming requests to prevent abuse.

### Register Blueprints
**Mechanic Blueprint (`/mechanics`):** Handles all mechanic-related API routes.
**Customer Blueprint (`/customers`):** Manages endpoints for customer operations.
**Service Ticket Blueprint (`/service-tickets`):** Handles service ticket creation and management.
**Inventory Blueprint (`/inventory`):** Provides endpoints for managing inventory items.

### Return the App
Returns the fully configured Flask application instance, ready to be run by the server (e.g., in `app.py`).

## pagination.py
### What This File Does
This file provides a helper function to **paginate SQLAlchemy query results** and return them in a standardized JSON format.

### paginate_query(query, schema, default_per_page=10)  
Handles pagination for large datasets, making it easier to display results across multiple pages in API responses.

### Pagination Parameters:
Reads `page` and `per_page` from the query parameters of an HTTP request.  
Defaults to page `1` and `10` items per page if not specified.

### Query Execution: 
Uses the provided SQLAlchemy query object to fetch the requested page of data.  
Ensures that missing or invalid page values don't result in errors.

### Serialization: 
Uses the provided Marshmallow schema to serialize the paginated results into JSON format.

### JSON Response:
Returns a structured JSON response containing:
`items`: Serialized data for the current page.
`total`: Total number of items.
`pages`: Total number of available pages.
`current_page`: The current page number.

## auth.py
### What This File Does
This file provides functions and decorators for **JSON Web Token (JWT) authentication** to secure API endpoints.

### encode_token(user_id) 
Generates a JWT token containing the user’s ID and an expiration time.
The token expires **1 hour** after being generated.
Encodes the payload using the application's `SECRET_KEY` and the HS256 algorithm.
**Use Case:**  
Typically called during login to issue a token for authenticated requests.

### token_required(f) 
A decorator that protects routes by requiring a valid JWT token.
**How It Works:**  
Checks for a token in the `Authorization` header (format: `Bearer <token>`).
Validates and decodes the token.
Extracts the `user_id` from the token payload and passes it to the wrapped function.
Returns appropriate error responses for:
Missing tokens (`401 Token is missing`).
Expired tokens (`401 Token expired`).
Invalid tokens (`401 Invalid token`).

### Security
The `SECRET_KEY` is loaded from environment variables (with a default fallback).
Token expiration ensures that old tokens cannot be reused indefinitely.

# Customer Blueprint Initialization

### __init__.py
### What This File Does
This file sets up the **Blueprint** for all customer-related routes in the Flask application.

### Creates a Blueprint
Defines a `customer` blueprint (`customer_bp`) which groups all customer-related endpoints.
This modular approach helps keep the application organized by separating routes into logical sections.

### Links Customer Routes
Imports the `routes` module after the blueprint is created.
This ensures that all routes defined in `routes.py` are registered under the `customer` blueprint.

### Why Use Blueprints
Blueprints allow for a cleaner, more maintainable structure, especially in large applications.
Customer-related APIs (e.g., registration, login, profile management) can be grouped together and registered with a URL prefix like `/customers`.

## routes.py
### What This File Does
This file defines all **customer-related API endpoints** within the Flask application. It handles customer management, authentication, and access to customer-specific resources such as service tickets.

### Customer Management
**Create Customer (`POST /customers/`)**  
Creates a new customer account.
Validates input data and ensures unique email registration.
Passwords are hashed before being stored.
  
**Get All Customers (`GET /customers/`)**  
Retrieves a paginated list of customers.
Requires authentication and supports caching for performance.
  
**Get Customer by ID (`GET /customers/<id>`)**  
Fetches details of a single customer by ID.
Requires authentication and caching.

**Update Customer (`PUT /customers/<id>`)**  
Updates customer details (e.g., name, email, password).
Passwords are rehashed if updated.
  
**Delete Customer (`DELETE /customers/<id>`)**  
Deletes a specific customer record by ID.

### Authentication
**Login (`POST /customers/login`)**  
Validates user credentials and issues a JWT token upon success.
Tokens are required to access protected endpoints.

### Customer-Specific Data
**Get My Tickets (`GET /customers/my-tickets`)**  
Returns a list of service ticket IDs belonging to the authenticated customer.

### Additional Features
**Rate Limiting:**  
Protects routes from abuse with limits (e.g., 10 requests per minute for login or customer creation).

**Caching:**  
Improves performance for customer list and customer detail endpoints.

**Error Handling:**  
Catches database errors, validation issues, and unexpected exceptions, returning structured JSON error messages.

## schemas.py
### What This File Does
This file defines **Marshmallow schemas** for serializing, deserializing, and validating customer-related data in the application. It ensures secure handling of sensitive information like passwords and provides validation for login.

### CustomerSchema
Maps the `Customer` model to a Marshmallow schema for automatic serialization and deserialization.
**Password Handling:**  
The `password` field is marked as `load_only`, meaning it can be provided when creating or updating a customer but will not appear in API responses.
**SQLAlchemy Integration:**  
Uses the `Customer` model and a SQLAlchemy session for validation and loading.
Allows creating (`load`) and reading (`dump`) `Customer` objects easily.

### LoginSchema
Designed for validating login requests.
**Fields:**
`email` – Must be a valid email and is required.
`password` – Required and `load_only` for security.
  
### Schema Instances
`customer_schema` – For handling single `Customer` objects.
`customers_schema` – For handling lists of `Customer` objects.
`login_schema` – For validating login data.

# Inventory Blueprint Initialization

## __init__.py
### What This File Does
This file sets up the **Blueprint** for all inventory-related routes in the Flask application.

### Creates the Inventory Blueprint
Defines a blueprint named `inventory_bp` for grouping all inventory-related API endpoints.
Assigns the URL prefix `/inventory` so all routes within this blueprint will start with this path.

### Links Inventory Routes
Imports the `routes` module after the blueprint is created.
This ensures that all inventory-related endpoints defined in `routes.py` are registered under the `/inventory` prefix.

### Why Use Blueprints
Blueprints allow for a cleaner, more maintainable structure, especially in large applications.  
Inventory-related APIs (e.g., adding, listing, or updating inventory items) can be grouped together and registered with a URL prefix like `/inventory`.

## routes.py
### What This File Does
This file defines all **inventory-related API endpoints** within the Flask application. It provides CRUD operations for managing parts and integrates authentication, caching, and rate limiting.

### Inventory Management
**Create Part (`POST /inventory/`)**
Adds a new part to the inventory.
Validates input data and saves it to the database.
Requires JWT authentication.

**Get All Parts (`GET /inventory/`)**  
Retrieves a list of all inventory parts.
Uses caching to improve performance.
Public endpoint.

**Get Part by ID (`GET /inventory/<id>`)**  
Fetches details of a specific part using its ID.
Uses caching for faster retrieval.
Public endpoint.

**Update Part (`PUT /inventory/<id>`)**  
Updates the details of an existing part.
Requires JWT authentication.
Handles partial updates of fields.

**Delete Part (`DELETE /inventory/<id>`)**  
Removes a part from the inventory.
Requires JWT authentication.

### Additional Features
**Rate Limiting:**  
Each route is limited to **5 requests per minute** to prevent abuse.
  
**Caching:**  
GET endpoints are cached for **120 seconds** to reduce database load.

**Error Handling:**  
Catches `IntegrityError`, `SQLAlchemyError`, and general exceptions.
Returns structured JSON error responses with status codes (e.g., 400, 404, 500).

### Authentication
JWT authentication (`token_required`) is applied to all **modifying endpoints** (create, update, delete).

## schemas.py
### What This File Does
This file defines **Marshmallow schemas** for serializing, deserializing, and validating inventory-related data. It maps the `Inventory` model to JSON format for API responses and input validation.

### InventorySchema
Maps the `Inventory` model to a Marshmallow schema for automatic serialization and deserialization.
`load_instance=True` – Allows creating and updating `Inventory` objects directly from validated input data.
`sqla_session=db.session` – Integrates with SQLAlchemy to validate and manage database operations.

### Schema Instances
`inventory_schema` – Used for handling single `Inventory` objects (e.g., creating or retrieving one part).
`inventories_schema` – Used for handling lists of `Inventory` objects (e.g., retrieving all parts).

# Mechanic Blueprint Initialization

## __init__.py
### What This File Does
This file sets up the **Blueprint** for all mechanic-related routes in the Flask application.

### Creates the Mechanic Blueprint
Defines a blueprint named `mechanic_bp` to group all mechanic-related API endpoints.
Assigns the URL prefix `/mechanics`, so all routes in this module will start with `/mechanics`.

### Links Mechanic Routes
Imports the `routes` module after the blueprint is created.
This ensures that all mechanic-related endpoints defined in `routes.py` are registered under the `/mechanics` prefix.
The delayed import helps avoid circular dependencies.

### Why Use Blueprints
Blueprints allow for a cleaner, more maintainable structure, especially in large applications.  
Mechanic-related APIs (e.g., adding mechanics, updating details, assigning tasks) can be grouped together and registered with a URL prefix like `/mechanics`.

## routes.py
### What This File Does
This file defines all **mechanic-related API endpoints** within the Flask application. It handles the creation, retrieval, updating, deletion, and authentication of mechanics while ensuring data security and performance optimization.

### Mechanic Management
**Create Mechanic (`POST /mechanics/`)**  
Creates a new mechanic record.
Validates unique email and securely hashes passwords before storing.

**Get All Mechanics (`GET /mechanics/`)**  
Retrieves a list of all mechanics.
Uses caching to reduce database load.
Passwords are excluded from the response.

**Get Mechanic by ID (`GET /mechanics/<id>`)**  
Retrieves details of a specific mechanic.
Caches responses for faster access.
Returns a `404` error if the mechanic is not found.

**Update Mechanic (`PUT /mechanics/<id>`)**  
Updates mechanic details.
Requires JWT authentication (`token_required`).
Hashes passwords on update.
Removes password from the response.

**Delete Mechanic (`DELETE /mechanics/<id>`)**  
Deletes a specific mechanic.
Requires JWT authentication.

**Top Mechanics (`GET /mechanics/top`)**  
Returns a list of mechanics sorted by the number of assigned service tickets.
Uses caching for performance.

### Authentication
**Mechanic Login (`POST /mechanics/login`)**  
Validates credentials.
Issues a JWT token for authenticated sessions.

### Additional Features
**Rate Limiting:**  
Routes are protected with rate limits (e.g., 10 per minute for creation/login, 50 per hour for reads).

**Caching:**  
GET requests are cached for **30 seconds** to improve response times.

**Error Handling:**  
Structured JSON error responses for `IntegrityError`, `SQLAlchemyError`, and unexpected exceptions.

### Security
Passwords are **hashed** before storage and never returned in responses.
JWT tokens are used for secure access to sensitive operations like updates and deletions.

## schemas.py
### What This File Does
This file defines **Marshmallow schemas** for serializing, deserializing, and validating mechanic-related data. It maps the `Mechanic` model to JSON format for API responses and input validation.

### MechanicSchema
Maps the `Mechanic` model to a Marshmallow schema for automatic serialization and deserialization.
`load_instance=True` – Allows creating and updating `Mechanic` objects directly from validated input data.
Automatically generates schema fields based on the `Mechanic` model.

### Schema Instances
`mechanic_schema`– For handling a single `Mechanic` object (e.g., creating or retrieving one mechanic).
`mechanics_schema`– For handling multiple `Mechanic` objects (e.g., listing all mechanics).

# Service Ticket Blueprint Initialization

## __init__.py
### What This File Does
This file sets up the **Blueprint** for all service ticket-related routes in the Flask application.

### Creates the Service Ticket Blueprint
Defines a blueprint named `service_ticket_bp` to group all service ticket-related API endpoints.
Assigns the URL prefix `/service-tickets`, so all routes in this module will start with `/service-tickets`.

### Links Service Ticket Routes
Imports the `routes` module after the blueprint is created.
This ensures that all service ticket-related endpoints defined in `routes.py` are registered under the `/service-tickets` prefix.

### Why Use Blueprints
Blueprints allow for a cleaner, more maintainable structure, especially in large applications.  
Service ticket-related APIs (e.g., creating, updating, and managing tickets) can be grouped together and registered with a URL prefix like `/service-tickets`.

## routes.py
### What This File Does
This file defines all **API endpoints** related to managing service tickets in the application.  
It handles creating, retrieving, updating, deleting tickets, as well as assigning mechanics and parts to tickets.

**Create Service Ticket (`POST /service-tickets/`)**  
Creates a new service ticket for the authenticated customer.  
Stores the ticket's description and links it to the current user.

**Get All Service Tickets (`GET /service-tickets/`)**  
Retrieves a list of all service tickets.  
Uses caching to improve performance.

**Get Service Ticket by ID (`GET /service-tickets/<ticket_id>`)**  
Fetches details of a specific ticket, including its assigned mechanics.  
Uses eager loading for better performance.

**Assign Mechanic (`PUT /service-tickets/<ticket_id>/assign-mechanic/<mechanic_id>`)**  
Assigns a mechanic to a specific service ticket.

**Remove Mechanic (`PUT /service-tickets/<ticket_id>/remove-mechanic/<mechanic_id>`)**  
Removes a mechanic from a specific service ticket.

**Edit Service Ticket (`PUT /service-tickets/<ticket_id>/edit`)**  
Updates ticket details, including:  
Editing the description.  
Bulk adding/removing mechanics.

**Delete Service Ticket (`DELETE /service-tickets/<ticket_id>`)**  
Deletes the specified service ticket.  
Requires JWT authentication.

**Add Parts to Ticket (`POST /service-tickets/<ticket_id>/add-parts`)**  
Attaches one or more inventory parts (e.g., car parts) to a service ticket.

**Remove Part from Ticket (`DELETE /service-tickets/<ticket_id>/remove-part/<part_id>`)**  
Removes a specific inventory part from a service ticket.

**Get Parts of Ticket (`GET /service-tickets/<ticket_id>/parts`)**  
Retrieves all inventory parts associated with a specific service ticket.

### Additional Features
**Rate Limiting:** Protects endpoints from abuse using Flask-Limiter.  
**Caching:** Improves read performance on frequently accessed data.  
**Error Handling:** Handles database errors, missing resources, and invalid input gracefully.  
**Authentication:** Uses token-based authentication (`token_required`) for protected endpoints.

## schemas.py
## What This File Does
This file defines **Marshmallow schemas** for serializing and deserializing `ServiceTicket` and `Mechanic` model data.  
These schemas ensure sensitive information like passwords is not exposed in API responses while enabling easy conversion between Python objects and JSON.

### MechanicSchema
Represents the `Mechanic` model data.
Excludes the `password` field from serialized output to ensure security.
Enables automatic field mapping from the SQLAlchemy model.

### ServiceTicketSchema
Represents the `ServiceTicket` model data.
Uses `mechanics = fields.Nested(MechanicSchema, many=True)` to include details of all mechanics linked to the service ticket.
Includes foreign key relationships (`include_fk = True`) for better representation of related data.
Supports loading data into a `ServiceTicket` instance (`load_instance = True`).

### Exported Schemas
`ticket_schema`: For serializing a single `ServiceTicket` object.
`tickets_schema`: For serializing multiple `ServiceTicket` objects (list format).


## Benefits of the Mechanic Shop
The Mechanic Shop application offers a comprehensive and efficient solution for managing automotive service operations. Below are some of the key benefits it provides:
### Streamlined Service Management
Centralizes customer, mechanic, and service ticket data in one platform.
Simplifies tracking of vehicle repair requests, and mechanic assignments.
### Improved Organization
Uses a modular design with Blueprints, making it easy to separate and maintain different parts of the application (customers, mechanics, service tickets).
Facilitates clear data relationships, such as many-to-many between mechanics and tickets.
### Efficient Resource Allocation
Allows assigning and removing mechanics to/from service tickets, optimizing workforce utilization.
Helps managers balance workloads and track mechanic specialties.
### Reliable Data Handling
Implements input validation and error handling to prevent duplicate records and maintain data integrity.
Uses Marshmallow schemas for easy data serialization and deserialization, ensuring consistent API responses.
### Scalable and Maintainable Architecture
Built with Flask’s Blueprint system to support modular growth as business needs evolve.
Clean separation of models, schemas, routes, and configurations supports long-term maintainability.
### User-Friendly API Design
Provides clear RESTful endpoints for CRUD operations on customers, mechanics, and tickets.
Returns meaningful HTTP status codes and error messages to facilitate frontend integration.
### Real-World Applicability
Designed to handle common automotive service shop scenarios, making it a practical tool for businesses of all sizes.
Enables easy extension to add features like invoicing, parts inventory, or appointment scheduling.

## Installation
Follow these steps to set up the application on your local machine:

### Clone the Repository
```bash
git clone https://github.com/chuks2274/pythonbe_final.git
cd shop-final

### Create and Activate a Virtual Environment
Run the following commands:
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

### Install Dependencies
Install all required Python packages using requirements.txt:
pip install -r requirements.txt

### Set Up Environment Variables
Create a .env file in the root directory and configure the following:
DATABASE_URL=your_database_connection_string
FLASK_ENV=development

## Usage
### Start the Flask Server
Run the Flask app:
python app.py

### The application will be available at:
http://127.0.0.1:5000

## Available Endpoints
The application provides RESTful APIs for customers, mechanics, and service tickets:
### Customers
POST /customers – Create a new customer
GET /customers – Fetch all customers
GET /customers/<id> – Fetch a single customer by ID
PUT /customers/<id> – Update a customer by ID
DELETE /customers/<id> – Delete a customer by ID
Get My Tickets (GET /customers/my-tickets) 
POST /customers/login – Customer login and JWT token generation
### Mechanics
POST /mechanics – Create a new mechanic
GET /mechanics – Fetch all mechanics
GET /mechanics/<id> – Fetch a single mechanic by ID
PUT /mechanics/<id> – Update a mechanic by ID
DELETE /mechanics/<id> – Delete a mechanic by ID
GET /mechanics/top – Get list of top mechanics by number of service tickets
POST /mechanics/login – Mechanic login and JWT token generation
### Service Tickets
POST /service-tickets – Create a new service ticket
GET /service-tickets – Fetch all tickets
GET /service-tickets/<id> – Fetch a ticket by ID
PUT /service-tickets/<id> – Update a ticket by ID
DELETE /service-tickets/<id> – Delete a ticket by ID
PUT /service-tickets/<ticket_id>/assign-mechanic/<mechanic_id> – Assign a mechanic
PUT /service-tickets/<ticket_id>/remove-mechanic/<mechanic_id> – Remove a mechanic
PUT /service-tickets/<ticket_id>/edit – Edit a service ticket (update description, add/remove mechanics)
POST /service-tickets/<ticket_id>/add-parts – Add parts (inventory items) to a service ticket
DELETE /service-tickets/<ticket_id>/remove-part/<part_id> – Remove a part from a service ticket
GET /service-tickets/<ticket_id>/parts – List all parts associated with a service ticket
### Inventory
POST /inventory/ – Create a new inventory part
GET /inventory/ – Retrieve all inventory parts
GET /inventory/<id> – Retrieve a specific inventory part by ID
PUT /inventory/<id> – Update a specific inventory part by ID
DELETE /inventory/<id> – Delete a specific inventory part by ID

## Contributing
Contributions, suggestions, and feedback are always welcome to help improve this project.
