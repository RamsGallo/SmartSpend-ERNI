# __init__.py

from flask import Flask, session
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL_ID = "gemini-2.5-flash-lite"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY') 
    app.config['API_KEY'] = os.getenv('SECRET_API_KEY')
    
    # Store the client object in the app's configuration
    # This is available from anywhere with `current_app.config['API_CLIENT']`
    app.config['API_CLIENT'] = genai.Client(api_key=app.config['API_KEY'])
    
    from board.pages import bp
    app.register_blueprint(bp)
    
    return app