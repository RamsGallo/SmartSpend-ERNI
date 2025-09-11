from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
import markdown
import os

from board.models import db, Transaction, User

bp = Blueprint("pages", __name__)

@bp.route("/")
def index():
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).all()

    income = sum(t.amount for t in transactions if t.type == "income")
    expense = sum(t.amount for t in transactions if t.type == "expense")
    balance = income - expense

    return render_template("pages/index.html", transactions=transactions, balance=balance)

@bp.route("/add", methods=["POST"])
def add_transaction():
    t_type = request.form["type"]
    amount = float(request.form["amount"])
    desc = request.form["description"]
    source = request.form.get("source", "N/A")

    # Assuming a hardcoded user for demonstration
    user = User.query.filter_by(username="testuser").first()
    if not user:
        # Create a test user if one doesn't exist
        user = User(username="testuser")
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()

    new_transaction = Transaction(
        type=t_type,
        amount=amount,
        description=desc,
        source=source,
        user_id=user.id
    )

    db.session.add(new_transaction)
    db.session.commit()

    return redirect(url_for("pages.index"))

@bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            return "Username already exists!"

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return "User created successfully! You can now log in."
    
    return """
        <form method="POST">
            <label for="username">Username:</label><br>
            <input type="text" id="username" name="username"><br>
            <label for="password">Password:</label><br>
            <input type="password" id="password" name="password"><br><br>
            <input type="submit" value="Register">
        </form>
    """

@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            return "Logged in successfully!"
        else:
            return "Invalid username or password."
    
    return """
        <form method="POST">
            <label for="username">Username:</label><br>
            <input type="text" id="username" name="username"><br>
            <label for="password">Password:</label><br>
            <input type="password" id="password" name="password"><br><br>
            <input type="submit" value="Log In">
        </form>
    """

@bp.route("/advice")
def advice():
    transactions = Transaction.query.all()

    if not transactions:
        return render_template("pages/advice.html", advice="No transactions yet. Add some first!")

    summary = "Here are my transactions:\n"
    for t in transactions:
        summary += f"{t.type} - ₱{t.amount} ({t.description})\n"

    client = current_app.config['API_CLIENT']
    
    model_id = "gemini-2.5-flash-lite"
    if "MODEL_ID" in current_app.config:
        model_id = current_app.config["MODEL_ID"]

    response = client.models.generate_content(
        model=model_id,
        contents=f"{summary}\nPlease give me short budgeting advice."
    )
    
    advice_text = markdown.markdown(response.text)
    return render_template("pages/advice.html", advice=advice_text)

@bp.route('/test')
def test_page():
    return render_template('pages/test.html')
