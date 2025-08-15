from werkzeug.security import generate_password_hash, check_password_hash # Import functions to hash passwords and verify password hashes
from .extensions import db # Import the database instance from extensions

# Link table for service tickets and mechanics (many-to-many)
service_mechanic = db.Table('service_mechanic',
    # Service ticket ID (FK to service_ticket), required
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_ticket.id'), nullable=False),
    # Mechanic ID (FK to mechanic), required
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanic.id'), nullable=False)
)

# Link table for service tickets and inventory parts (many-to-many)
service_inventory = db.Table('service_inventory',
    # Service ticket ID column, references service_ticket table, required
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_ticket.id'), nullable=False),
    # Inventory ID column, references inventory table, required
    db.Column('inventory_id', db.Integer, db.ForeignKey('inventory.id'), nullable=False)
)


# Define the Customer database model (table)
class Customer(db.Model):
    __tablename__ = 'customer'   
    
    id = db.Column(db.Integer, primary_key=True)   
    name = db.Column(db.String(100), nullable=False)   
    email = db.Column(db.String(100), unique=True, nullable=False)   
    password = db.Column(db.String(255), nullable=False)   
    address = db.Column(db.String(200), nullable=False)   
    phone = db.Column(db.String(20), nullable=False)   
    # One-to-many relationship: customer has many service tickets
    service_tickets = db.relationship('ServiceTicket', backref='customer')


# Define the Mechanic database model (table)
class Mechanic(db.Model):
    __tablename__ = 'mechanic'   
    
    id = db.Column(db.Integer, primary_key=True)   
    name = db.Column(db.String(100), nullable=False)   
    email = db.Column(db.String(120), nullable=False)   
    password = db.Column(db.String(255), nullable=False)  
    address = db.Column(db.String(200), nullable=False)   
    phone = db.Column(db.String(20), nullable=False)   
    specialty = db.Column(db.String(100), nullable=False)   
    salary = db.Column(db.Float, nullable=False)   
    # Relationship: Many-to-many between mechanics and service tickets via association table
    service_tickets = db.relationship('ServiceTicket', secondary=service_mechanic, back_populates='mechanics')
    
    # Hash and set the user's password securely
    def set_password(self, password):
        self.password = generate_password_hash(password)   
    
    # Check if the provided password matches the stored hashed password
    def check_password(self, password):
        return check_password_hash(self.password, password)   


# Define the ServiceTicket database model (table)
class ServiceTicket(db.Model):
    __tablename__ = 'service_ticket'   
    
    id = db.Column(db.Integer, primary_key=True)   
    description = db.Column(db.String(255), nullable=False)   
    vin = db.Column(db.String(17), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)   
    # Many-to-many relationship: mechanics assigned to service tickets
    mechanics = db.relationship('Mechanic', secondary=service_mechanic, back_populates='service_tickets')
    # Many-to-many relationship: inventory parts used in service tickets
    parts = db.relationship('Inventory', secondary=service_inventory, back_populates='tickets')


# Define the Inventory database model (table)
class Inventory(db.Model):
    __tablename__ = 'inventory' 
    
    id = db.Column(db.Integer, primary_key=True)   
    name = db.Column(db.String(100), nullable=False)  
    sku = db.Column(db.String(50), unique=True, nullable=False)   
    description = db.Column(db.String(255), nullable=True)   
    price = db.Column(db.Float, nullable=False)   
    # Many-to-many relationship: parts linked to service tickets
    tickets = db.relationship('ServiceTicket', secondary=service_inventory, back_populates='parts')