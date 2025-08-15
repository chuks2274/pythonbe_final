# Mechanic Workshop API

This project provides a RESTful API for managing a mechanic workshop, including Customers, Mechanics, Service Tickets, and Inventory. The API is documented using Swagger 2.0 and supports secure endpoints via JWT-based authentication.

## Features

- **Customer Management**: Register, authenticate, update, delete, and retrieve customer information.
- **Mechanic Management**: Register mechanics, authenticate, manage mechanic profiles, and view top-performing mechanics.
- **Service Tickets**: Create, assign mechanics/parts, and manage repair service tickets.
- **Inventory Management**: CRUD operations on parts used in repairs.
- **JWT Authentication**: Secure endpoints for authorized users (both customers and mechanics).
- **Pagination Support**: Most list endpoints support pagination via `?page=1&per_page=10`.

## API Documentation

Swagger UI can be used to explore the API.

**Base URL:**  
http://localhost:5000/api

### Authentication

All protected routes require a JWT token in the `Authorization` header using the format:
Authorization: Bearer <your_token>

## Endpoints

### Customers

| Method | Endpoint                      | Description                       |
|--------|-------------------------------|-----------------------------------|
| POST   | `/customers`                  | Create Customer                   |
| POST   | `/customers/login`            | Customer Login (Token Auth)       |
| GET    | `/customers/`                 | Find All Customers (Paginated)    |
| GET    | `/customers/{id}`             | Find Customer by ID               |
| PUT    | `/customers/{id}`             | Update Customer by ID             |
| DELETE | `/customers/{id}`             | Delete Customer by ID             |
| GET    | `/customers/my-tickets`       | Find Service Tickets              |

### Mechanics

| Method | Endpoint                            | Description                        |
|--------|-------------------------------------|------------------------------------|
| POST   | `/mechanics`                        | Create Mechanic                    |
| POST   | `/mechanics/login`                  | Mechanic Login (Token Auth)        |
| GET    | `/mechanics/`                       | Find All Mechanics (Paginated)     |
| GET    | `/mechanics/{id}`                   | Find Mechanic by ID                |
| PUT    | `/mechanics/{id}`                   | Update Mechanic by ID              |
| DELETE | `/mechanics/{id}`                   | Delete Mechanic by ID              |
| GET    | `/mechanics/top`                    | Find Top Mechanics                 |

### Service Tickets

| Method | Endpoint                            | Description                        |
|--------|-------------------------------------|------------------------------------|
| POST   | `/service-tickets`  | Create Service Ticket                                 
| GET    | `/service-tickets/` | Find All Service Tickets (Paginated)    
| GET    | `/service-tickets/{id}`  | Find Service Ticket by ID                
| PUT    | `/service-tickets/{id}`  | Update service ticket by ID                   
| DELETE |  `/service-tickets/{id}` | Delete Service Ticket by ID                    
| PUT    | `/service-tickets/{ticket_id}/assign-mechanic/{mechanic_id}` | Assign Mechanic to Service Ticket by ID
| PUT    |  `/service-tickets/{ticket_id}/remove-mechanic/{mechanic_id}` | Remove Mechanic from Service Ticket by ID
| PUT    | `/service-tickets/{ticket_id}/edit`      | Edit Mechanics on Service Ticket by ID 
| POST   | `/service-tickets/{ticket_id}/add-parts` | Add Parts to Service Ticket by ID           
| GET    |  `/service-tickets/{ticket_id}/parts`    | Find Parts on Service Ticket by ID               
| DELETE |  `/service-tickets/{ticket_id}/remove-part/{part_id}` | Remove Parts from Service Ticket by ID

### Inventory

| Method | Endpoint            | Description                          |
|--------|---------------------|--------------------------------------|
| POST   | `/inventory`        | Create Part                          |
| GET    | `/inventory/`       | Find All Parts (Paginated)           |
| GET    | `/inventory/{id}`   | Find Part by ID                      |
| PUT    | `/inventory/{id}`   | Update Part by ID                    |
| DELETE | `/inventory/{id}`   | Delete Part by ID                    |

## Security

All non-auth endpoints (e.g., create user, login) are public. All other endpoints are secured via JWT.

- Use the login endpoint to retrieve a token.
- Attach the token to requests using the `Authorization` header:
Authorization: Bearer <your_token>

## Definitions

The API uses the following object definitions:

- `Customer`, `CustomerInput`
- `Mechanic`, `MechanicInput`
- `ServiceTicket`, `ServiceTicketInput`
- `Inventory`, `InventoryInput`

These definitions specify the required fields and types for creating or returning data objects.

## How to View Swagger UI

To view the Swagger documentation in a browser:

1. Start the Flask server (`flask run` or however your project is configured).
2. Visit: http://localhost:5000/docs

*(Make sure your app serves Swagger UI at this path)*

## Built With

- Flask + Flask-Restful
- Swagger 2.0 (OpenAPI Specification)
- JWT Authentication
- SQLAlchemy (ORM)
- Marshmallow (Validation)

## License

This project is intended for educational purposes 