from application.extensions import ma # Import Marshmallow instance (used for serialization and validation)
from application.models import Mechanic # Import the Mechanic model (this is the table we want to turn into JSON)
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema # Import base class for auto-generating schema from SQLAlchemy models


# Schema to serialize/deserialize Mechanic objects.
class MechanicSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic # Mechanic model.
        load_instance = True # Load data as model instance.


mechanic_schema = MechanicSchema() # Schema for single mechanic
mechanics_schema = MechanicSchema(many=True)  # Schema for multiple mechanics