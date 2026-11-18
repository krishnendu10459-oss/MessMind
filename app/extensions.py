from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy and Flask-Migrate extensions
db = SQLAlchemy()
migrate = Migrate()
