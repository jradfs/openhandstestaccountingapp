from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    name = db.Column(db.String(100))
    role = db.Column(db.String(20))  # admin, staff, client
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    clients = db.relationship('Client', backref='manager', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(200), nullable=False)
    business_type = db.Column(db.String(50))
    tax_id = db.Column(db.String(20))
    fiscal_year_end = db.Column(db.Date)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transactions = db.relationship('Transaction', backref='client', lazy=True)
    financial_statements = db.relationship('FinancialStatement', backref='client', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(500))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(50))  # debit or credit
    category = db.Column(db.String(100))
    account = db.Column(db.String(100))
    reference = db.Column(db.String(100))
    status = db.Column(db.String(20))  # pending, processed, reviewed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    name = db.Column(db.String(100), nullable=False)
    number = db.Column(db.String(20))
    type = db.Column(db.String(50))  # asset, liability, equity, revenue, expense
    category = db.Column(db.String(50))
    balance = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FinancialStatement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    type = db.Column(db.String(50))  # balance_sheet, income_statement, cash_flow
    period_start = db.Column(db.Date)
    period_end = db.Column(db.Date)
    data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    generated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    due_date = db.Column(db.Date)
    priority = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pending')
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100))
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)