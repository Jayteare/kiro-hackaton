"""
Expense model for the expense tracker application.
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import validates
from app import db


class Expense(db.Model):
    """
    Expense model representing a single expense entry.
    
    Attributes:
        id: Primary key identifier
        amount: Expense amount (must be positive)
        description: Description of the expense (required, max 255 chars)
        category: Expense category (defaults to "Uncategorized")
        date: Date of the expense (defaults to current timestamp)
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
    """
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(
        db.Numeric(10, 2), 
        nullable=False,
        doc="Expense amount in decimal format"
    )
    description = db.Column(
        db.String(255), 
        nullable=False,
        doc="Description of the expense"
    )
    category = db.Column(
        db.String(100), 
        nullable=False, 
        default="Uncategorized",
        doc="Expense category"
    )
    date = db.Column(
        db.DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        doc="Date when the expense occurred"
    )
    created_at = db.Column(
        db.DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        doc="Record creation timestamp"
    )
    updated_at = db.Column(
        db.DateTime, 
        nullable=False, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        doc="Record last update timestamp"
    )
    
    # Database constraints
    __table_args__ = (
        CheckConstraint('amount > 0', name='positive_amount'),
        CheckConstraint('length(description) > 0', name='non_empty_description'),
    )
    
    def __init__(self, amount=None, description=None, category=None, date=None, **kwargs):
        """Initialize expense with proper defaults."""
        # Set defaults before validation
        if category is None or category == "":
            category = "Uncategorized"
        if date is None:
            date = datetime.utcnow()
            
        # Call parent constructor which will trigger validators
        super().__init__(
            amount=amount,
            description=description,
            category=category,
            date=date,
            **kwargs
        )
    
    @validates('amount')
    def validate_amount(self, key, amount):
        """Validate that amount is positive."""
        if amount is None:
            raise ValueError("Amount is required")
        
        # Convert to Decimal for precise validation
        if isinstance(amount, (int, float)):
            amount = Decimal(str(amount))
        elif not isinstance(amount, Decimal):
            try:
                amount = Decimal(str(amount))
            except (ValueError, TypeError, Exception):
                raise ValueError("Amount must be a valid number")
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        return amount
    
    @validates('description')
    def validate_description(self, key, description):
        """Validate description is not empty and within length limits."""
        if not description or not description.strip():
            raise ValueError("Description is required")
        
        description = description.strip()
        if len(description) > 255:
            raise ValueError("Description must be 255 characters or less")
        
        return description
    
    @validates('category')
    def validate_category(self, key, category):
        """Validate and normalize category."""
        if not category or (isinstance(category, str) and not category.strip()):
            return "Uncategorized"
        
        if isinstance(category, str):
            category = category.strip()
        else:
            category = str(category).strip()
            
        if len(category) > 100:
            raise ValueError("Category must be 100 characters or less")
        
        return category if category else "Uncategorized"
    
    @validates('date')
    def validate_date(self, key, date):
        """Validate date is a datetime object."""
        if date is None:
            return datetime.utcnow()
        
        if not isinstance(date, datetime):
            raise ValueError("Date must be a datetime object")
        
        return date
    
    def __repr__(self):
        """String representation of the expense."""
        return (f"<Expense(id={self.id}, amount={self.amount}, "
                f"description='{self.description}', category='{self.category}', "
                f"date={self.date})>")
    
    def to_dict(self):
        """Convert expense to dictionary representation."""
        return {
            'id': self.id,
            'amount': float(self.amount) if self.amount else None,
            'description': self.description,
            'category': self.category,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }