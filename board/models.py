from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# IMPORTANT: Remove the line below that re-creates the db object.
# db = SQLAlchemy()

# Instead, import the db object that was created in the main __init__.py
from . import db


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    source = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def set_password(self, password):
        """Hashes the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks the provided password against the hashed password."""
        return check_password_hash(self.password_hash, password)
