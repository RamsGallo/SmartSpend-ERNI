import os
import secrets
import tempfile
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash
from flask_login import login_required, login_user, logout_user, current_user
import markdown
import requests
from sqlalchemy import func
from datetime import datetime
from werkzeug.utils import secure_filename
from board.models import db, Transaction, User, Goal
from board.ocr_utils import process_image_for_ocr, parse_transaction_from_text

bp = Blueprint("pages", __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/")
@login_required
def index():
    # Only show transactions for the currently logged-in user
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).all()
    
    # Fetch goals for the current user and order them by priority
    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.priority.desc()).all()

    # Convert the list of SQLAlchemy objects into a list of dictionaries
    # This makes the data JSON-serializable for the JavaScript in the template
    transactions_for_json = [
        {
            'description': t.description,
            'amount': t.amount,
            'type': t.type,
            'source': t.source,
            'created_at': t.created_at.isoformat()
        }
        for t in transactions
    ]

    income = sum(t.amount for t in transactions if t.type == "income")
    expense = sum(t.amount for t in transactions if t.type == "expense")
    balance = income - expense

    # Pass the JSON-serializable list and goals to the template
    return render_template("pages/index.html", 
        transactions=transactions_for_json, 
        balance=balance, 
        income=income, 
        expense=expense,
        goals=goals
    )

@bp.route("/add", methods=["POST"])
@login_required
def add_transaction():
    t_type = request.form["type"] 
    amount = float(request.form["amount"])
    desc = request.form["description"]
    source = request.form.get("source", "N/A")

    # Use the current_user provided by Flask-Login
    new_transaction = Transaction(
        type=t_type,
        amount=amount,
        description=desc,
        source=source,
        user_id=current_user.id
    )

    db.session.add(new_transaction)
    db.session.commit()

    return redirect(url_for("pages.index"))

# New route to add a financial goal
@bp.route("/add_goal", methods=["POST"])
@login_required
def add_goal():
    name = request.form["name"]
    target_amount = float(request.form["target_amount"])
    priority = int(request.form["priority"])

    new_goal = Goal(
        name=name,
        target_amount=target_amount,
        priority=priority,
        user_id=current_user.id
    )

    db.session.add(new_goal)
    db.session.commit()

    flash("Goal added successfully!", "success")
    return redirect(url_for("pages.index"))

# New route to distribute the remaining balance based on goals
@bp.route("/distribute_balance", methods=["POST"])
@login_required
def distribute_balance():
    # Calculate the user's current balance
    income = db.session.query(func.sum(Transaction.amount)).filter_by(user_id=current_user.id, type='income').scalar() or 0
    expense = db.session.query(func.sum(Transaction.amount)).filter_by(user_id=current_user.id, type='expense').scalar() or 0
    balance = income - expense

    if balance <= 0:
        flash("No balance to distribute.", "warning")
        return redirect(url_for("pages.index"))

    # Get all goals for the user
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    total_priority = sum(goal.priority for goal in goals)

    if total_priority == 0:
        flash("No goals with priorities set.", "warning")
        return redirect(url_for("pages.index"))

    distributed_amount = 0
    for goal in goals:
        # Calculate the proportional amount to distribute to this goal
        proportion = goal.priority / total_priority
        amount_to_distribute = balance * proportion
        
        # Ensure we don't exceed the target amount
        if goal.current_amount + amount_to_distribute > goal.target_amount:
            amount_to_distribute = goal.target_amount - goal.current_amount
        
        if amount_to_distribute > 0:
            goal.current_amount += amount_to_distribute
            distributed_amount += amount_to_distribute

            # Create a new "expense" transaction for the distribution
            new_transaction = Transaction(
                type='expense',
                amount=amount_to_distribute,
                description=f"Distributed to goal: {goal.name}",
                source='Goal Distribution',
                user_id=current_user.id
            )
            db.session.add(new_transaction)

    db.session.commit()
    flash(f"Successfully distributed ₱{distributed_amount:.2f} to your goals!", "success")
    return redirect(url_for("pages.index"))

@bp.route("/ocr_upload", methods=["POST"])
@login_required
def ocr_upload():
    if "file" not in request.files:
        flash("No file uploaded.", "danger")
        return redirect(url_for("pages.index"))

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected.", "danger")
        return redirect(url_for("pages.index"))

    # Save the uploaded file temporarily
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Run OCR
    extracted_text = process_image_for_ocr(filepath)
    transactions = parse_transaction_from_text(extracted_text)

    if not transactions:
        flash("No transaction details found in scan.", "warning")
        return redirect(url_for("pages.index"))

    # Save each transaction for the logged-in user
    for tx in transactions:
        new_tx = Transaction(
            type=tx["type"],
            amount=tx["amount"],
            description=tx["description"],
            source=tx["source"],
            user_id=current_user.id,  # ✅ tie to logged-in user
        )
        db.session.add(new_tx)

    db.session.commit()

    flash(f"Added {len(transactions)} transaction(s) from OCR scan!", "success")
    return redirect(url_for("pages.index"))


@bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        full_name = request.form['full_name']
        email = request.form['email']
        date_of_birth = request.form['date_of_birth']
        age = request.form['age']
        income_source = request.form['income_source']

        if User.query.filter_by(username=username).first():
            flash('Username already exists! Please choose a different one.', 'error')
            return redirect(url_for('pages.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered! Please use a different one.', 'error')
            return redirect(url_for('pages.register'))

        try:
            dob_obj = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            age_int = int(age)

            new_user = User(
                username=username,
                full_name=full_name,
                email=email,
                date_of_birth=dob_obj,
                age=age_int,
                income_source=income_source
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user)

            flash('Registration successful and you have been logged in!', 'success')
            return redirect(url_for('pages.index'))
        
        except ValueError:
            flash('Invalid date or age format. Please check your inputs.', 'error')
            return redirect(url_for('pages.register'))

    return render_template('auth/register.html')
            
@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_input = request.form['username']
        password = request.form['password']
        
        user = User.query.filter((User.username == user_input) | (User.email == user_input)).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            flash('Login successful!', 'success')

            next_page = request.args.get('next')
            return redirect(next_page or url_for('pages.index'))
        
        else:
            flash('Invalid credentials. Please try again.', 'error')
            return redirect(url_for('pages.login'))
            
    return render_template('auth/login.html')

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('pages.login'))

@bp.route("/advice")
@login_required
def advice():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    # Create a summary of transactions
    transaction_summary = "Here are my transactions:\n"
    for t in transactions:
        transaction_summary += f"{t.type} - ₱{t.amount} ({t.description})\n"

    # Add profile information for personalization
    profile_info = (
        f"My name is {current_user.full_name}, and my source of income is {current_user.income_source}. "
        f"I am {current_user.age} years old."
    )
    
    full_prompt = (
        f"{transaction_summary}\n\n"
        f"Based on this transaction history, and the following personal information:\n"
        f"{profile_info}\n\n"
        f"Please give me some smart and personalized budgeting advice."
    )

    client = current_app.config['API_CLIENT']
    
    model_id = "gemini-2.5-flash-lite"
    if "MODEL_ID" in current_app.config:
        model_id = current_app.config["MODEL_ID"]

    response = client.models.generate_content(
        model=model_id,
        contents=full_prompt
    )
    
    advice_text = markdown.markdown(response.text)
    return render_template("pages/advice.html", advice=advice_text)

@bp.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_income_source = request.form.get('income_source')
        if new_income_source:
            current_user.income_source = new_income_source
            db.session.commit()
            flash('Income source updated successfully!', 'success')
        return redirect(url_for('pages.profile'))
    
    return render_template('pages/profile.html', user=current_user)

@bp.route("/investments")
@login_required
def investments():
    # Initialize investments in the session if it doesn't exist
    if 'investments' not in session:
        session['investments'] = []
    
    # Pass the investments from the session to the template
    return render_template("pages/investment_tracker.html", holdings=session['investments'])

# Create an API endpoint to fetch stock data
@bp.route("/api/stock/<symbol>")
@login_required
def get_stock_data(symbol):
    # Retrieve the API key from the app configuration
    api_key = current_app.config.get('ALPHA_VANTAGE_API_KEY')
    
    if not api_key:
        return {"error": "API key not configured."}, 500

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "Error Message" in data:
            return {"error": data["Error Message"]}, 400

        quote = data.get('Global Quote', {})
        if not quote:
            return {"error": f"No data found for symbol: {symbol}"}, 404

        stock_data = {
            "symbol": quote.get('01. symbol'),
            "price": float(quote.get('05. price')),
            "daily_change": float(quote.get('09. change'))
        }
        return stock_data

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Request failed for {symbol}: {e}")
        return {"error": "Failed to fetch stock data."}, 500

# Route to add a new investment to the session
@bp.route("/add_investment", methods=["POST"])
@login_required
def add_investment():
    symbol = request.form["symbol"].upper()
    quantity = float(request.form["quantity"])

    if quantity <= 0:
        flash("Quantity must be a positive number.", "error")
        return redirect(url_for("pages.investments"))

    # Update or add the investment to the session list
    found = False

    if "investments" not in session:
        session["investments"] = []

    for item in session['investments']:
        if item['symbol'] == symbol:
            item['quantity'] += quantity
            found = True
            break
    
    if not found:
        session['investments'].append({
            'symbol': symbol,
            'quantity': quantity
        })

    # The session needs to be modified for Flask to save changes.
    session.modified = True
    return render_template("investment_tracker.html", holdings=session["investments"])

# Route to remove an investment from the session
@bp.route("/remove_investment", methods=["POST"])
@login_required
def remove_investment():
    symbol_to_remove = request.form['symbol'].upper()
    session['investments'] = [
        item for item in session['investments'] if item['symbol'] != symbol_to_remove
    ]
    session.modified = True
    flash("Investment removed successfully!", "success")
    return redirect(url_for("pages.investments"))