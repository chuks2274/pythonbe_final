from application.extensions import ma, db # Import Marshmallow (ma) and database session (db) from your extensions setup.
from application.models import Inventory  # Import the Inventory model so we can create a schema for it.
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema # Import a Marshmallow base class that helps create schemas from SQLAlchemy models automatically.

# Schema for Inventory model serialization/deserialization
class InventorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory   # Use Inventory model
        load_instance = True   # Enable deserialization into model instances
        sqla_session = db.session   # Use this SQLAlchemy session for DB operations  

inventory_schema = InventorySchema() # Schema for a single Inventory item
inventories_schema = InventorySchema(many=True) # Schema for multiple Inventory items