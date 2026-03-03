from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    auth0_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    quotes = db.relationship('Quote', backref='user', lazy=True)
    policies = db.relationship('Policy', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)
    claims = db.relationship('Claim', backref='user', lazy=True)
    

class InsuranceProduct(db.Model):
    __tablename__ = 'insurance_products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    coverage_details = db.Column(db.Text)
    base_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    quotes = db.relationship('Quote', backref='product', lazy=True)
    policies = db.relationship('Policy', backref='product', lazy=True)

class Quote(db.Model):
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    quote_number = db.Column(db.String(50), unique=True, default=lambda: f"Q{str(uuid.uuid4())[:8].upper()}")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('insurance_products.id'), nullable=False)
    
    # Quote details
    coverage_amount = db.Column(db.Float)
    deductible = db.Column(db.Float)
    additional_options = db.Column(db.JSON)
    
    # Calculated values
    calculated_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Accepted, Expired
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationship
    policy = db.relationship('Policy', backref='quote', uselist=False, lazy=True)

class Policy(db.Model):
    __tablename__ = 'policies'
    
    id = db.Column(db.Integer, primary_key=True)
    policy_number = db.Column(db.String(50), unique=True, default=lambda: f"POL{str(uuid.uuid4())[:8].upper()}")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('insurance_products.id'), nullable=False)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False)
    
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    premium_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Active')  # Active, Expired, Cancelled
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    claims = db.relationship('Claim', backref='policy', lazy=True)
    payments = db.relationship('Payment', backref='policy', lazy=True)

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, default=lambda: f"TXN{str(uuid.uuid4())[:8].upper()}")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    policy_id = db.Column(db.Integer, db.ForeignKey('policies.id'), nullable=False)
    
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50))  # Credit Card, Bank Transfer, etc.
    status = db.Column(db.String(20), default='Completed')  # Pending, Completed, Failed
    
    receipt_url = db.Column(db.String(500))

class Claim(db.Model):
    __tablename__ = 'claims'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_number = db.Column(db.String(50), unique=True, default=lambda: f"CLM{str(uuid.uuid4())[:8].upper()}")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    policy_id = db.Column(db.Integer, db.ForeignKey('policies.id'), nullable=False)
    
    incident_date = db.Column(db.DateTime, nullable=False)
    filing_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    claim_amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='Submitted')  # Submitted, Under Review, Approved, Rejected
    
    documents = db.Column(db.JSON)  # Store references to uploaded documents
    approved_amount = db.Column(db.Float)
    resolution_date = db.Column(db.DateTime)