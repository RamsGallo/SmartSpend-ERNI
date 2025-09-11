from flask import Flask, render_template, request, redirect, url_for, session
import os
from dotenv import load_dotenv
from IPython.display import Markdown
import markdown
from google import genai
from google.genai import types
load_dotenv()

# Access the API key from the environment
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_ID = "gemini-2.5-flash-lite"

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for session



if __name__ == "__main__":
    app.run(debug=True)
