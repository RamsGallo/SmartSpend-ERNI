# pages.py

from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
import markdown
import os

bp = Blueprint("pages", __name__)

@bp.route("/")
def index():
    if "transactions" not in session:
        session["transactions"] = []
    transactions = session["transactions"]

    income = sum(t["amount"] for t in transactions if t["type"] == "income")
    expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
    balance = income - expense

    return render_template("pages/index.html", transactions=transactions, balance=balance)

@bp.route("/add", methods=["POST"])
def add_transaction():
    t_type = request.form["type"]
    amount = float(request.form["amount"])
    desc = request.form["description"]

    transaction = {"type": t_type, "amount": amount, "description": desc}
    session["transactions"].append(transaction)
    session.modified = True

    return redirect(url_for("pages.index"))

@bp.route("/advice")
def advice():
    transactions = session.get("transactions", [])

    if not transactions:
        return render_template("advice.html", advice="No transactions yet. Add some first!")

    summary = "Here are my transactions:\n"
    for t in transactions:
        summary += f"{t['type']} - ₱{t['amount']} ({t['description']})\n"

    # Get the client from the current application context
    client = current_app.config['API_CLIENT']
    
    # Check if a model has been defined in __init__.py
    model_id = "gemini-1.5-flash"  # Default model if not found
    if "MODEL_ID" in current_app.config:
        model_id = current_app.config["MODEL_ID"]

    # Ask Gemini for budgeting advice
    response = client.models.generate_content(
        model=model_id,
        contents=f"{summary}\nPlease give me short budgeting advice."
    )
    
    advice_text = markdown.markdown(response.text)
    return render_template("pages/advice.html", advice=advice_text)

@bp.route('/test')
def test_page():
    return render_template('pages/test.html')