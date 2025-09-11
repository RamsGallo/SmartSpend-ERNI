import os
from flask import Flask, session
from dotenv import load_dotenv
from google import genai
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

load_dotenv()

# Create the database instance
db = SQLAlchemy()

# Create the migration engine
migrate = Migrate()

MODEL_ID = "gemini-2.5-flash-lite"

def create_app():
    app = Flask(__name__, instance_path=os.path.join(os.getcwd(), 'var', 'board-instance'))
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY') 
    app.config['API_KEY'] = os.getenv('SECRET_API_KEY')
    app.config['MODEL_ID'] = MODEL_ID

    # Create the instance path directory if it doesn't exist
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Set the database URI to the path within the instance folder
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "app.db")

    # Initialize the database and migration engine with the app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import models to ensure they are registered with SQLAlchemy
    from . import models
    
    # Store the client object in the app's configuration
    # This is available from anywhere with `current_app.config['API_CLIENT']`
    app.config['API_CLIENT'] = genai.Client(api_key=app.config['API_KEY'])
    
    from board.pages import bp
    app.register_blueprint(bp)
    
    return app
