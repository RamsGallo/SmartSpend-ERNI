# SmartSpend-ERNI
ERNI Hackathon 2025 Fintech

SmartSpend is an AI-empowered budgeting app with tools such as OCR for quick income/expense inputs and an AI advisor that suggests personalized devises for better budgeting!

Disclaimer: This system is neither meant for commercial use nor dedicated for commercial distribution. 

Getting Started
This section will help you get a copy of the project up and running on your local machine.

Prerequisites
Before you begin, ensure you have the following installed:

Python 3.x: You can download it from the official Python website.
pip: The Python package installer, which usually comes with Python 3.
git: To clone the repository. You can get it from the official Git website.

Clone repository
'''git clone https://github.com/RamsGallo/SmartSpend-ERNI.git
cd SmartSpend-ERNI'''

Install required dependencies
'''pip install -r requirements.txt'''

Set board as the Flask app root
'''set FLASK_APP=board'''

Setup SQAlchemy database
'''flask db init'''

Migrate database
'''flask db migrate -m "comment_here"'''

Implement migration
'''flask db upgrade'''

Set up environment variables
Create a .env file in the project's root directory and add the necessary variables.
'''FLASK_SECRET_KEY="your_secret_key"'''
'''GEMENI_SECRET_KEY="your_secret_key"''' 

Run the Flask app
'''flask run --host=0.0.0.0 (optional) --port=8080 (optional) --debug (optional)'''

AI tools and Libraries Used:
- Gemini 2.5 for personalized 
- EasyOCR for character recognition

Roles of each team member:
Cathlene Ilagan - Project design
Rams Gallo - Fullstack
Joshua Gagarin - API Integration and backend


