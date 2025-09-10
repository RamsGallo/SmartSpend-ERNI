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

@app.route("/")
def index():
    if "transactions" not in session:
        session["transactions"] = []
    transactions = session["transactions"]

    # calculate balance
    income = sum(t["amount"] for t in transactions if t["type"] == "income")
    expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
    balance = income - expense

    return render_template("index.html", transactions=transactions, balance=balance)

@app.route("/add", methods=["POST"])
def add_transaction():
    t_type = request.form["type"]
    amount = float(request.form["amount"])
    desc = request.form["description"]

    transaction = {"type": t_type, "amount": amount, "description": desc}
    session["transactions"].append(transaction)
    session.modified = True

    return redirect(url_for("index"))

@app.route("/advice")
def advice():
    transactions = session.get("transactions", [])

    if not transactions:
        return render_template("advice.html", advice="No transactions yet. Add some first!")

    # prepare summary for AI
    summary = "Here are my transactions:\n"
    for t in transactions:
        summary += f"{t['type']} - ₱{t['amount']} ({t['description']})\n"
    print(summary)
    # ask Gemini for budgeting advice
    # model = genai.GenerativeModel("gemini-1.5-flash")
    # response = model.generate_content(f"{summary}\nPlease give me budgeting advice.")
    response = client.models.generate_content(
    model=MODEL_ID,
    contents=f"{summary}\nPlease give me short budgeting advice."
)
    

    advice_text = markdown.markdown(response.text)
    # print(advice_text)
    return render_template("advice.html", advice=advice_text)

if __name__ == "__main__":
    app.run(debug=True)
