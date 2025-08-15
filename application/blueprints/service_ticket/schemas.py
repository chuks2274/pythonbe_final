from application.extensions import ma # Import Marshmallow instance from extensions to create schemas
from application.models import ServiceTicket, Mechanic, Inventory # Import database models for ServiceTicket, Mechanic, and Inventory
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema # Import Marshmallow's SQLAlchemy helper to auto-generate schemas from models
from marshmallow import fields # Import fields to define nested relationships in schemas


# Schema for serializing and deserializing Mechanic objects
class MechanicSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic           # Schema linked to Mechanic model
        load_instance = True       # Enable deserialization into model instances
        exclude = ("password",)    # Exclude password field from serialized output


# Schema for Inventory (parts)
class InventorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory           # Schema for Inventory model
        load_instance = True        # Enable deserialization into model instances


# Schema for ServiceTicket including nested mechanics and parts
class ServiceTicketSchema(SQLAlchemyAutoSchema):
    
    # Include list of mechanic details in tickets
    mechanics = fields.Nested(MechanicSchema, many=True)

    # Include list of parts (inventory items) in tickets
    parts = fields.Nested(InventorySchema, many=True)  
    

    class Meta:
        model = ServiceTicket       # Use ServiceTicket model
        load_instance = True        # Enable deserialization into model instances
        include_fk = True           # Include foreign key fields in output

ticket_schema = ServiceTicketSchema()  # Schema for a single service ticket
tickets_schema = ServiceTicketSchema(many=True) # Schema for multiple service tickets