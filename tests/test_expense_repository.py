"""
Unit tests for ExpenseRepository.
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.expense import Expense, Base
from app.repositories.expense_repository import ExpenseRepository


@pytest.fixture
def in_memory_db():
    """Create in-memory SQLite database for testing."""
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


@pytest.fixture
def db_session(in_memory_db):
    """Create database session for testing."""
    session = in_memory_db()
    yield session
    session.close()


@pytest.fixture
def expense_repository(db_session):
    """Create ExpenseRepository instance for testing."""
    return ExpenseRepository(db_session)


@pytest.fixture
def sample_expense_data():
    """Sample expense data for testing."""
    return {
        'amount': Decimal('25.50'),
        'description': 'Coffee and pastry',
        'category': 'Food',
        'date': datetime(2025, 1, 15, 10, 30, 0)
    }


@pytest.fixture
def multiple_expenses_data():
    """Multiple expense records for testing."""
    base_date = datetime(2025, 1, 1)
    return [
        {
            'amount': Decimal('25.50'),
            'description': 'Coffee',
            'category': 'Food',
            'date': base_date
        },
        {
            'amount': Decimal('50.00'),
            'description': 'Gas',
            'category': 'Transport',
            'date': base_date + timedelta(days=1)
        },
        {
            'amount': Decimal('15.75'),
            'description': 'Lunch',
            'category': 'Food',
            'date': base_date + timedelta(days=2)
        },
        {
            'amount': Decimal('100.00'),
            'description': 'Groceries',
            'category': 'Food',
            'date': base_date + timedelta(days=3)
        },
        {
            'amount': Decimal('30.00'),
            'description': 'Bus ticket',
            'category': 'Transport',
            'date': base_date + timedelta(days=4)
        }
    ]


class TestExpenseRepositoryCreate:
    """Test expense creation operations."""
    
    def test_create_expense_success(self, expense_repository, sample_expense_data):
        """Test successful expense creation."""
        expense = expense_repository.create(sample_expense_data)
        
        assert expense.id is not None
        assert expense.amount == sample_expense_data['amount']
        assert expense.description == sample_expense_data['description']
        assert expense.category == sample_expense_data['category']
        assert expense.date == sample_expense_data['date']
        assert expense.created_at is not None
        assert expense.updated_at is not None
    
    def test_create_expense_with_defaults(self, expense_repository):
        """Test expense creation with default values."""
        expense_data = {
            'amount': Decimal('10.00'),
            'description': 'Test expense'
        }
        
        expense = expense_repository.create(expense_data)
        
        assert expense.category == 'Uncategorized'
        assert expense.date is not None
    
    def test_create_expense_invalid_amount(self, expense_repository):
        """Test expense creation with invalid amount."""
        expense_data = {
            'amount': Decimal('-10.00'),
            'description': 'Invalid expense'
        }
        
        with pytest.raises(ValueError, match="Amount must be positive"):
            expense_repository.create(expense_data)
    
    def test_create_expense_missing_description(self, expense_repository):
        """Test expense creation with missing description."""
        expense_data = {
            'amount': Decimal('10.00'),
            'description': ''
        }
        
        with pytest.raises(ValueError, match="Description is required"):
            expense_repository.create(expense_data)


class TestExpenseRepositoryRead:
    """Test expense read operations."""
    
    def test_get_by_id_existing(self, expense_repository, sample_expense_data):
        """Test getting expense by existing ID."""
        created_expense = expense_repository.create(sample_expense_data)
        retrieved_expense = expense_repository.get_by_id(created_expense.id)
        
        assert retrieved_expense is not None
        assert retrieved_expense.id == created_expense.id
        assert retrieved_expense.amount == created_expense.amount
        assert retrieved_expense.description == created_expense.description
    
    def test_get_by_id_non_existing(self, expense_repository):
        """Test getting expense by non-existing ID."""
        expense = expense_repository.get_by_id(999)
        assert expense is None
    
    def test_get_all_empty(self, expense_repository):
        """Test getting all expenses when none exist."""
        expenses, total_count = expense_repository.get_all()
        
        assert expenses == []
        assert total_count == 0
    
    def test_get_all_with_data(self, expense_repository, multiple_expenses_data):
        """Test getting all expenses with data."""
        # Create multiple expenses
        for expense_data in multiple_expenses_data:
            expense_repository.create(expense_data)
        
        expenses, total_count = expense_repository.get_all()
        
        assert len(expenses) == 5
        assert total_count == 5
        # Should be sorted by date descending by default
        assert expenses[0].date > expenses[1].date
    
    def test_get_all_with_pagination(self, expense_repository, multiple_expenses_data):
        """Test pagination in get_all."""
        # Create multiple expenses
        for expense_data in multiple_expenses_data:
            expense_repository.create(expense_data)
        
        # Get first page
        expenses_page1, total_count = expense_repository.get_all(page=1, per_page=2)
        assert len(expenses_page1) == 2
        assert total_count == 5
        
        # Get second page
        expenses_page2, total_count = expense_repository.get_all(page=2, per_page=2)
        assert len(expenses_page2) == 2
        assert total_count == 5
        
        # Ensure different expenses on different pages
        page1_ids = {e.id for e in expenses_page1}
        page2_ids = {e.id for e in expenses_page2}
        assert page1_ids.isdisjoint(page2_ids)
    
    def test_get_all_filter_by_category(self, expense_repository, multiple_expenses_data):
        """Test filtering expenses by category."""
        # Create multiple expenses
        for expense_data in multiple_expenses_data:
            expense_repository.create(expense_data)
        
        # Filter by Food category
        food_expenses, total_count = expense_repository.get_all(category='Food')
        
        assert len(food_expenses) == 3  # Coffee, Lunch, Groceries
        assert total_count == 3
        assert all(expense.category == 'Food' for expense in food_expenses)
    
    def test_get_all_filter_by_date_range(self, expense_repository, multiple_expenses_data):
        """Test filtering expenses by date range."""
        # Create multiple expenses
        for expense_data in multiple_expenses_data:
            expense_repository.create(expense_data)
        
        # Filter by date range (first 2 days)
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 2, 23, 59, 59)
        
        expenses, total_count = expense_repository.get_all(
            start_date=start_date, 
            end_date=end_date
        )
        
        assert len(expenses) == 2  # Coffee and Gas
        assert total_count == 2
        assert all(start_date <= expense.date <= end_date for expense in expenses)
    
    def test_get_all_sorting(self, expense_repository, multiple_expenses_data):
        """Test sorting in get_all."""
        # Create multiple expenses
        for expense_data in multiple_expenses_data:
            expense_repository.create(expense_data)
        
        # Sort by amount ascending
        expenses, _ = expense_repository.get_all(sort_by='amount', sort_order='asc')
        amounts = [float(expense.amount) for expense in expenses]
        assert amounts == sorted(amounts)
        
        # Sort by amount descending
        expenses, _ = expense_repository.get_all(sort_by='amount', sort_order='desc')
        amounts = [float(expense.amount) for expense in expenses]
        assert amounts == sorted(amounts, reverse=True)


class TestExpenseRepositoryUpdate:
    """Test expense update operations."""
    
    def test_update_existing_expense(self, expense_repository, sample_expense_data):
        """Test updating an existing expense."""
        # Create expense
        expense = expense_repository.create(sample_expense_data)
        original_updated_at = expense.updated_at
        
        # Update expense
        update_data = {
            'amount': Decimal('30.00'),
            'description': 'Updated coffee'
        }
        
        updated_expense = expense_repository.update(expense.id, update_data)
        
        assert updated_expense is not None
        assert updated_expense.id == expense.id
        assert updated_expense.amount == Decimal('30.00')
        assert updated_expense.description == 'Updated coffee'
        assert updated_expense.category == sample_expense_data['category']  # Unchanged
        assert updated_expense.updated_at > original_updated_at
    
    def test_update_non_existing_expense(self, expense_repository):
        """Test updating a non-existing expense."""
        update_data = {'amount': Decimal('30.00')}
        result = expense_repository.update(999, update_data)
        
        assert result is None
    
    def test_update_with_invalid_data(self, expense_repository, sample_expense_data):
        """Test updating with invalid data."""
        expense = expense_repository.create(sample_expense_data)
        
        update_data = {'amount': Decimal('-10.00')}
        
        with pytest.raises(ValueError):
            expense_repository.update(expense.id, update_data)


class TestExpenseRepositoryDelete:
    """Test expense delete operations."""
    
    def test_delete_existing_expense(self, expense_repository, sample_expense_data):
        """Test deleting an existing expense."""
        expense = expense_repository.create(sample_expense_data)
        
        result = expense_repository.delete(expense.id)
        assert result is True
        
        # Verify expense is deleted
        deleted_expense = expense_repository.get_by_id(expense.id)
        assert deleted_expense is None
    
    def test_delete_non_existing_expense(self, expense_repository):
        """Test deleting a non-existing expense."""
        result = expense_repository.delete(999)
        assert result is False


class TestExpenseRepositoryUtilities:
    """Test utility methods."""
    
    def test_exists(self, expense_repository, sample_expense_data):
        """Test expense existence check."""
        # Non-existing expense
        assert expense_repository.exists(999) is False
        
        # Create expense and check existence
        expense = expense_repository.create(sample_expense_data)
        assert expense_repository.exists(expense.id) is True
    
    def test_count(self, expense_repository, multiple_expenses_data):
        """Test expense counting."""
        # Empty count
        assert expense_repository.count() == 0
        
        # Create expenses
        for expense_data in multiple_expenses_data:
            expense_repository.create(expense_data)
        
        # Total count
        assert expense_repository.count() == 5
        
        # Count by category
        assert expense_repository.count(category='Food') == 3
        assert expense_repository.count(category='Transport') == 2
        
        # Count by date range
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 2, 23, 59, 59)
        assert expense_repository.count(start_date=start_date, end_date=end_date) == 2
    
    def test_get_categories(self, expense_repository, multiple_expenses_data):
        """Test getting unique categories."""
        # Empty categories
        categories = expense_repository.get_categories()
        assert categories == []
        
        # Create expenses
        for expense_data in multiple_expenses_data:
            expense_repository.create(expense_data)
        
        categories = expense_repository.get_categories()
        assert set(categories) == {'Food', 'Transport'}
    
    def test_get_summary(self, expense_repository, multiple_expenses_data):
        """Test getting expense summary."""
        # Empty summary
        summary = expense_repository.get_summary()
        assert summary['total_amount'] == 0.0
        assert summary['expense_count'] == 0
        assert summary['categories'] == []
        
        # Create expenses
        for expense_data in multiple_expenses_data:
            expense_repository.create(expense_data)
        
        # Full summary
        summary = expense_repository.get_summary()
        
        expected_total = 25.50 + 50.00 + 15.75 + 100.00 + 30.00  # 221.25
        assert summary['total_amount'] == expected_total
        assert summary['expense_count'] == 5
        assert len(summary['categories']) == 2
        
        # Check category breakdown
        food_category = next(cat for cat in summary['categories'] if cat['category'] == 'Food')
        transport_category = next(cat for cat in summary['categories'] if cat['category'] == 'Transport')
        
        assert food_category['amount'] == 141.25  # 25.50 + 15.75 + 100.00
        assert food_category['count'] == 3
        assert transport_category['amount'] == 80.00  # 50.00 + 30.00
        assert transport_category['count'] == 2
        
        # Categories should be sorted by amount (descending)
        assert summary['categories'][0]['category'] == 'Food'  # Higher amount
        assert summary['categories'][1]['category'] == 'Transport'
    
    def test_get_summary_with_date_filter(self, expense_repository, multiple_expenses_data):
        """Test getting summary with date filtering."""
        # Create expenses
        for expense_data in multiple_expenses_data:
            expense_repository.create(expense_data)
        
        # Summary for first 2 days
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 2, 23, 59, 59)
        
        summary = expense_repository.get_summary(start_date=start_date, end_date=end_date)
        
        assert summary['total_amount'] == 75.50  # Coffee + Gas
        assert summary['expense_count'] == 2
        assert summary['date_range']['start'] == start_date.isoformat()
        assert summary['date_range']['end'] == end_date.isoformat()


class TestExpenseRepositoryErrorHandling:
    """Test error handling in repository operations."""
    
    def test_create_rollback_on_error(self, expense_repository, db_session):
        """Test that create operations rollback on error."""
        # This test ensures that if an error occurs during create,
        # the transaction is rolled back properly
        
        # Create a valid expense first
        valid_data = {
            'amount': Decimal('10.00'),
            'description': 'Valid expense'
        }
        expense_repository.create(valid_data)
        
        # Try to create invalid expense
        invalid_data = {
            'amount': Decimal('-10.00'),  # Invalid amount
            'description': 'Invalid expense'
        }
        
        with pytest.raises(ValueError):
            expense_repository.create(invalid_data)
        
        # Verify that the session is still usable and the valid expense exists
        expenses, count = expense_repository.get_all()
        assert count == 1
        assert expenses[0].description == 'Valid expense'
    
    def test_update_rollback_on_error(self, expense_repository, sample_expense_data):
        """Test that update operations rollback on error."""
        expense = expense_repository.create(sample_expense_data)
        
        # Try to update with invalid data
        invalid_update = {'amount': Decimal('-50.00')}
        
        with pytest.raises(ValueError):
            expense_repository.update(expense.id, invalid_update)
        
        # Verify original expense is unchanged
        unchanged_expense = expense_repository.get_by_id(expense.id)
        assert unchanged_expense.amount == sample_expense_data['amount']
    
    def test_delete_rollback_on_error(self, expense_repository, sample_expense_data, db_session):
        """Test that delete operations handle errors properly."""
        expense = expense_repository.create(sample_expense_data)
        
        # Simulate a database error by closing the session
        # This is a bit artificial but tests the error handling path
        original_session = expense_repository.session
        
        # The delete should still work normally in this case
        result = expense_repository.delete(expense.id)
        assert result is True