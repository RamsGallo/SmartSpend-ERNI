SmartSpend-ERNI
A hackathon project for the ERNI Hackathon 2025 Fintech

SmartSpend is an AI-empowered budgeting application that helps users manage their finances. Key features include OCR (Optical Character Recognition) for quick income and expense inputs and an AI advisor that provides personalized financial advice for better budgeting.

Disclaimer: This system is not intended for commercial use or distribution.

Getting Started
This section will guide you through the process of getting a copy of the project up and running on your local machine.

Prerequisites
Before you begin, ensure you have the following software installed:

Python 3.x: You can download it from the official Python website.

pip: The Python package installer, which typically comes with Python 3.

git: To clone the repository. You can download it from the official Git website.

Installation
Clone the repository:

Bash

git clone https://github.com/RamsGallo/SmartSpend-ERNI.git
cd SmartSpend-ERNI
Install required dependencies:
This command will install all the necessary libraries, including Flask, from the requirements.txt file.

Bash

pip install -r requirements.txt
Set up environment variables:
Create a .env file in the project's root directory and add the following variables.

Bash

FLASK_SECRET_KEY="your_secret_key"
GEMINI_SECRET_KEY="your_secret_key"
Configure the Flask app root:

Bash

set FLASK_APP=board
Set up the SQLAlchemy database:
Follow these steps to initialize and migrate the database.

Bash

flask db init
flask db migrate -m "comment_here"
flask db upgrade
Run the Flask application:

Bash

flask run --host=0.0.0.0 --port=8080 --debug
Note: The --host, --port, and --debug flags are optional.

AI Tools and Libraries Used
Gemini 2.5: Utilized for providing personalized financial advice.

EasyOCR: Used for the Optical Character Recognition feature to quickly scan and input expenses/incomes.

Team Members
Cathlene Ilagan: Project design

Rams Gallo: Full-stack development

Joshua Gagarin: API integration and backend development
