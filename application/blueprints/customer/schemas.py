from application.extensions import ma, db # Import `ma` (Marshmallow object) and `db` (SQLAlchemy database) from the extensions file.
from application.models import Customer # Import the Customer model so we can build a schema for it.
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema # Import the base class to create a schema from an SQLAlchemy model automatically.
from marshmallow import fields # Import fields to define what type of data each schema field will accept.

# Schema for serializing (output) and deserializing (input) Customer model data
class CustomerSchema(SQLAlchemyAutoSchema):
    
    # Define password field that is used only when loading data 
    password = fields.String(load_only=True)  

    class Meta:
        model = Customer   # Auto-generate fields from Customer model
        load_instance = True   # Deserialize into Customer object
        sqla_session = db.session  # Use this DB session for load/validation
        exclude = []  # No fields excluded

# Schema for validating login input only
class LoginSchema(ma.Schema):
    
    # Email is a required field and must be a valid email address
    email = fields.Email(required=True)  
    
    # Password is required on input but never included in output responses
    password = fields.String(required=True, load_only=True)  

customer_schema = CustomerSchema()  # Schema for a single customer
customers_schema = CustomerSchema(many=True) # Schema for multiple customers

login_schema = LoginSchema()  # Schema to validate login data