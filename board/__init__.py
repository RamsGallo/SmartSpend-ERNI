import os
from flask import Flask, session
from dotenv import load_dotenv
from google import genai
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

load_dotenv()

# Create the database instance
db = SQLAlchemy()

# Create the migration engine
migrate = Migrate()

# Create the Login Manager instance
login_manager = LoginManager()

MODEL_ID = "gemini-2.5-flash-lite"

def create_app():
    app = Flask(__name__, instance_path=os.path.join(os.getcwd(), 'var', 'board-instance'))
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
    app.config['API_KEY'] = os.getenv('SECRET_API_KEY')
    app.config['MODEL_ID'] = MODEL_ID
    app.config['ALPHA_VANTAGE_API_KEY'] = os.getenv('ALPHA_VANTAGE_API_KEY')

    os.makedirs(app.instance_path, exist_ok=True)

    upload_folder = os.path.join(app.instance_path, "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = upload_folder

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "app.db")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'pages.login'

    from . import models

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))
    
    app.config['API_CLIENT'] = genai.Client(api_key=app.config['API_KEY'])

    from board.pages import bp
    app.register_blueprint(bp)
    
    return app
