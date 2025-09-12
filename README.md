# SmartSpend-ERNI

**A hackathon project for the ERNI Hackathon 2025 Fintech**

SmartSpend is an AI-empowered budgeting application that helps users manage their finances. Key features include **OCR** (Optical Character Recognition) for quick income and expense inputs and an **AI advisor** that provides personalized financial advice for better budgeting.

**Disclaimer:** This system is not intended for commercial use or distribution.

---

### **Getting Started**

This section will guide you through the process of getting a copy of the project up and running on your local machine.

#### **Prerequisites**

Before you begin, ensure you have the following software installed:

* **Python 3.x:** You can download it from the [official Python website](https://www.python.org/downloads/).
* **pip:** The Python package installer, which typically comes with Python 3.
* **git:** To clone the repository. You can download it from the [official Git website](https://git-scm.com/downloads/).

#### **Installation**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/RamsGallo/SmartSpend-ERNI.git
    cd SmartSpend-ERNI
    ```

2.  **Install required dependencies:**
    This command will install all the necessary libraries, including Flask, from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the project's root directory and add the following variables.
    ```bash
    FLASK_SECRET_KEY="your_secret_key"
    GEMINI_SECRET_KEY="your_secret_key"
    ```

4.  **Configure the Flask app root:**
    ```bash
    set FLASK_APP=board
    ```

5.  **Set up the SQLAlchemy database:**
    Follow these steps to initialize and migrate the database.
    ```bash
    flask db init
    flask db migrate -m "comment_here"
    flask db upgrade
    ```

6.  **Run the Flask application:**
    ```bash
    flask run --host=0.0.0.0 --port=8080 --debug
    ```
    _Note: The `--host`, `--port`, and `--debug` flags are optional._

---

### **AI Tools and Libraries Used**

* **Gemini 2.5**: Utilized for providing personalized financial advice.
* **EasyOCR**: Used for the Optical Character Recognition feature to quickly scan and input expenses/incomes. EasyOCR requires PyTorch and Numpy

---

### **Team Members**

* **Cathlene Ilagan**: Project design
* **Rams Gallo**: Full-stack development
* **Joshua Gagarin**: API integration and backend development
