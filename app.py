from flask import Flask
from models import db
from routes import bp
import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Configure PostgreSQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', '')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the app
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Register the blueprint
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)