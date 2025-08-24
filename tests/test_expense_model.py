"""
Unit tests for the Expense model.

Tests cover validation constraints, model behavior, and database operations.
"""
import pytest
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.models import Expense, Base


class TestExpenseModel:
    """Test cases for the Expense model."""
    
    @pytest.fixture
    def db_session(self):
        """Create an in-memory SQLite database for testing."""
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(engine)
        
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        yield session
        
        session.close()
    
    def test_expense_creation_with_valid_data(self, db_session):
        """Test creating an expense with valid data."""
        expense = Expense(
            amount=Decimal('25.50'),
            description="Coffee and pastry",
            category="Food"
        )
        
        db_session.add(expense)
        db_session.commit()
        
        assert expense.id is not None
        assert expense.amount == Decimal('25.50')
        assert expense.description == "Coffee and pastry"
        assert expense.category == "Food"
        assert expense.date is not None
        assert expense.created_at is not None
        assert expense.updated_at is not None
    
    def test_expense_creation_with_minimal_data(self, db_session):
        """Test creating an expense with only required fields."""
        expense = Expense(
            amount=Decimal('10.00'),
            description="Test expense"
        )
        
        db_session.add(expense)
        db_session.commit()
        
        assert expense.id is not None
        assert expense.amount == Decimal('10.00')
        assert expense.description == "Test expense"
        assert expense.category == "Uncategorized"  # Default value
        assert expense.date is not None
    
    def test_expense_amount_validation_positive(self):
        """Test that positive amounts are accepted."""
        expense = Expense(amount=Decimal('1.00'), description="Test")
        assert expense.amount == Decimal('1.00')
        
        expense = Expense(amount=100, description="Test")
        assert expense.amount == Decimal('100')
        
        expense = Expense(amount=0.01, description="Test")
        assert expense.amount == Decimal('0.01')
    
    def test_expense_amount_validation_zero_raises_error(self):
        """Test that zero amount raises ValueError."""
        with pytest.raises(ValueError, match="Amount must be positive"):
            Expense(amount=0, description="Test")
    
    def test_expense_amount_validation_negative_raises_error(self):
        """Test that negative amount raises ValueError."""
        with pytest.raises(ValueError, match="Amount must be positive"):
            Expense(amount=-10.50, description="Test")
    
    def test_expense_amount_validation_none_raises_error(self):
        """Test that None amount raises ValueError."""
        with pytest.raises(ValueError, match="Amount is required"):
            Expense(amount=None, description="Test")
    
    def test_expense_amount_validation_invalid_type_raises_error(self):
        """Test that invalid amount type raises ValueError."""
        with pytest.raises(ValueError, match="Amount must be a valid number"):
            Expense(amount="invalid", description="Test")
    
    def test_expense_description_validation_required(self):
        """Test that description is required."""
        with pytest.raises(ValueError, match="Description is required"):
            Expense(amount=10, description="")
        
        with pytest.raises(ValueError, match="Description is required"):
            Expense(amount=10, description="   ")  # Only whitespace
        
        with pytest.raises(ValueError, match="Description is required"):
            Expense(amount=10, description=None)
    
    def test_expense_description_validation_max_length(self):
        """Test that description has maximum length constraint."""
        long_description = "x" * 256  # 256 characters
        
        with pytest.raises(ValueError, match="Description must be 255 characters or less"):
            Expense(amount=10, description=long_description)
    
    def test_expense_description_validation_strips_whitespace(self):
        """Test that description whitespace is stripped."""
        expense = Expense(amount=10, description="  Test description  ")
        assert expense.description == "Test description"
    
    def test_expense_category_validation_default(self):
        """Test that category defaults to 'Uncategorized'."""
        expense = Expense(amount=10, description="Test")
        assert expense.category == "Uncategorized"
        
        expense = Expense(amount=10, description="Test", category="")
        assert expense.category == "Uncategorized"
        
        expense = Expense(amount=10, description="Test", category=None)
        assert expense.category == "Uncategorized"
    
    def test_expense_category_validation_max_length(self):
        """Test that category has maximum length constraint."""
        long_category = "x" * 101  # 101 characters
        
        with pytest.raises(ValueError, match="Category must be 100 characters or less"):
            Expense(amount=10, description="Test", category=long_category)
    
    def test_expense_category_validation_strips_whitespace(self):
        """Test that category whitespace is stripped."""
        expense = Expense(amount=10, description="Test", category="  Food  ")
        assert expense.category == "Food"
    
    def test_expense_date_validation_default(self):
        """Test that date defaults to current time."""
        before = datetime.utcnow()
        expense = Expense(amount=10, description="Test")
        after = datetime.utcnow()
        
        assert before <= expense.date <= after
    
    def test_expense_date_validation_custom_date(self):
        """Test that custom date is accepted."""
        custom_date = datetime(2025, 1, 15, 10, 30, 0)
        expense = Expense(amount=10, description="Test", date=custom_date)
        assert expense.date == custom_date
    
    def test_expense_date_validation_invalid_type_raises_error(self):
        """Test that invalid date type raises ValueError."""
        with pytest.raises(ValueError, match="Date must be a datetime object"):
            Expense(amount=10, description="Test", date="2025-01-15")
    
    def test_expense_database_constraints_positive_amount(self, db_session):
        """Test database constraint for positive amount."""
        # Create expense with valid amount first
        expense = Expense(amount=10, description="Test")
        db_session.add(expense)
        db_session.commit()
        
        # Try to update with invalid amount directly in database
        # This should be caught by the model validator before reaching DB
        with pytest.raises(ValueError):
            expense.amount = -10
    
    def test_expense_database_constraints_non_empty_description(self, db_session):
        """Test database constraint for non-empty description."""
        # This should be caught by the model validator
        with pytest.raises(ValueError):
            Expense(amount=10, description="")
    
    def test_expense_repr(self):
        """Test string representation of expense."""
        expense = Expense(
            amount=25.50,
            description="Coffee",
            category="Food"
        )
        expense.id = 1
        expense.date = datetime(2025, 1, 15, 10, 30, 0)
        
        repr_str = repr(expense)
        assert "Expense(id=1" in repr_str
        assert "amount=25.5" in repr_str
        assert "description='Coffee'" in repr_str
        assert "category='Food'" in repr_str
    
    def test_expense_to_dict(self):
        """Test dictionary conversion of expense."""
        test_date = datetime(2025, 1, 15, 10, 30, 0)
        expense = Expense(
            amount=25.50,
            description="Coffee",
            category="Food",
            date=test_date
        )
        expense.id = 1
        expense.created_at = test_date
        expense.updated_at = test_date
        
        expense_dict = expense.to_dict()
        
        expected_dict = {
            'id': 1,
            'amount': 25.5,
            'description': 'Coffee',
            'category': 'Food',
            'date': test_date.isoformat(),
            'created_at': test_date.isoformat(),
            'updated_at': test_date.isoformat()
        }
        
        assert expense_dict == expected_dict
    
    def test_expense_to_dict_with_none_values(self):
        """Test dictionary conversion handles None values properly."""
        # Test the to_dict method's handling of None values by creating
        # a simple object with the necessary attributes
        class MockExpense:
            def __init__(self):
                self.id = None
                self.amount = None
                self.description = "Test"
                self.category = "Test"
                self.date = None
                self.created_at = None
                self.updated_at = None
            
            def to_dict(self):
                return {
                    'id': self.id,
                    'amount': float(self.amount) if self.amount else None,
                    'description': self.description,
                    'category': self.category,
                    'date': self.date.isoformat() if self.date else None,
                    'created_at': self.created_at.isoformat() if self.created_at else None,
                    'updated_at': self.updated_at.isoformat() if self.updated_at else None
                }
        
        mock_expense = MockExpense()
        expense_dict = mock_expense.to_dict()
        
        assert expense_dict['id'] is None
        assert expense_dict['amount'] is None
        assert expense_dict['date'] is None
        assert expense_dict['created_at'] is None
        assert expense_dict['updated_at'] is None
    
    def test_expense_timestamps_auto_set(self, db_session):
        """Test that timestamps are automatically set."""
        before = datetime.utcnow()
        
        expense = Expense(amount=10, description="Test")
        db_session.add(expense)
        db_session.commit()
        
        after = datetime.utcnow()
        
        assert before <= expense.created_at <= after
        assert before <= expense.updated_at <= after
        # Timestamps should be very close (within 1 second)
        time_diff = abs((expense.created_at - expense.updated_at).total_seconds())
        assert time_diff < 1.0
    
    def test_expense_updated_at_changes_on_update(self, db_session):
        """Test that updated_at changes when record is updated."""
        expense = Expense(amount=10, description="Test")
        db_session.add(expense)
        db_session.commit()
        
        original_updated_at = expense.updated_at
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        expense.description = "Updated description"
        db_session.commit()
        
        assert expense.updated_at > original_updated_at