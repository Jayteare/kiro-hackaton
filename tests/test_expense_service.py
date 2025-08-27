"""
Unit tests for ExpenseService business logic and validation.
"""
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from app.services.expense_service import (
    ExpenseService, 
    ExpenseServiceError, 
    ValidationError, 
    NotFoundError
)
from app.models.expense import Expense
from app.repositories.expense_repository import ExpenseRepository


# Global fixtures for all test classes
@pytest.fixture
def mock_session():
    """Create a mock database session."""
    return Mock(spec=Session)

@pytest.fixture
def mock_repository():
    """Create a mock expense repository."""
    return Mock(spec=ExpenseRepository)

@pytest.fixture
def expense_service(mock_session):
    """Create an ExpenseService instance with mocked dependencies."""
    return ExpenseService(mock_session)

@pytest.fixture
def sample_expense_data():
    """Sample expense data for testing."""
    return {
        'amount': '25.50',
        'description': 'Coffee and pastry',
        'category': 'Food',
        'date': datetime.now(timezone.utc).isoformat()  # Convert to ISO string
    }

@pytest.fixture
def sample_expense():
    """Sample expense object for testing."""
    return Expense(
        id=1,
        amount=Decimal('25.50'),
        description='Coffee and pastry',
        category='Food',
        date=datetime.now(timezone.utc)
    )


class TestExpenseService:
    """Test cases for ExpenseService class."""


class TestCreateExpense:
    """Test cases for expense creation."""
    
    def test_create_expense_success(self, expense_service, sample_expense_data, sample_expense):
        """Test successful expense creation."""
        # Mock repository create method
        expense_service.repository.create = Mock(return_value=sample_expense)
        
        result = expense_service.create_expense(sample_expense_data)
        
        assert result == sample_expense
        expense_service.repository.create.assert_called_once()
    
    def test_create_expense_with_default_category(self, expense_service, sample_expense):
        """Test expense creation with default category."""
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee and pastry'
            # No category provided
        }
        
        expense_service.repository.create = Mock(return_value=sample_expense)
        
        result = expense_service.create_expense(expense_data)
        
        # Verify that repository.create was called with "Uncategorized" category
        call_args = expense_service.repository.create.call_args[0][0]
        assert call_args['category'] == 'Uncategorized'
    
    def test_create_expense_with_empty_category(self, expense_service, sample_expense):
        """Test expense creation with empty category."""
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee and pastry',
            'category': '   '  # Empty/whitespace category
        }
        
        expense_service.repository.create = Mock(return_value=sample_expense)
        
        result = expense_service.create_expense(expense_data)
        
        # Verify that repository.create was called with "Uncategorized" category
        call_args = expense_service.repository.create.call_args[0][0]
        assert call_args['category'] == 'Uncategorized'
    
    def test_create_expense_category_title_case(self, expense_service, sample_expense):
        """Test that category is converted to title case."""
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee and pastry',
            'category': 'food and drinks'
        }
        
        expense_service.repository.create = Mock(return_value=sample_expense)
        
        result = expense_service.create_expense(expense_data)
        
        # Verify that category is converted to title case
        call_args = expense_service.repository.create.call_args[0][0]
        assert call_args['category'] == 'Food And Drinks'
    
    def test_create_expense_invalid_amount(self, expense_service):
        """Test expense creation with invalid amount."""
        expense_data = {
            'amount': '-10.00',  # Negative amount
            'description': 'Invalid expense'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            expense_service.create_expense(expense_data)
        
        assert "Validation failed" in str(exc_info.value)
    
    def test_create_expense_missing_required_fields(self, expense_service):
        """Test expense creation with missing required fields."""
        expense_data = {
            'amount': '25.50'
            # Missing description
        }
        
        with pytest.raises(ValidationError) as exc_info:
            expense_service.create_expense(expense_data)
        
        assert "Validation failed" in str(exc_info.value)
    
    def test_create_expense_empty_description(self, expense_service):
        """Test expense creation with empty description."""
        expense_data = {
            'amount': '25.50',
            'description': '   '  # Empty/whitespace description
        }
        
        with pytest.raises(ValidationError) as exc_info:
            expense_service.create_expense(expense_data)
        
        assert "Validation failed" in str(exc_info.value)
    
    def test_create_expense_amount_precision(self, expense_service, sample_expense):
        """Test that amount is rounded to 2 decimal places."""
        expense_data = {
            'amount': '25.555',  # 3 decimal places
            'description': 'Test expense'
        }
        
        expense_service.repository.create = Mock(return_value=sample_expense)
        
        result = expense_service.create_expense(expense_data)
        
        # Verify that amount is rounded to 2 decimal places
        call_args = expense_service.repository.create.call_args[0][0]
        assert call_args['amount'] == Decimal('25.56')
    
    def test_create_expense_repository_error(self, expense_service, sample_expense_data):
        """Test handling of repository errors during creation."""
        expense_service.repository.create = Mock(side_effect=Exception("Database error"))
        
        with pytest.raises(ExpenseServiceError) as exc_info:
            expense_service.create_expense(sample_expense_data)
        
        assert "Failed to create expense" in str(exc_info.value)


class TestGetExpense:
    """Test cases for expense retrieval."""
    
    def test_get_expense_success(self, expense_service, sample_expense):
        """Test successful expense retrieval."""
        expense_service.repository.get_by_id = Mock(return_value=sample_expense)
        
        result = expense_service.get_expense(1)
        
        assert result == sample_expense
        expense_service.repository.get_by_id.assert_called_once_with(1)
    
    def test_get_expense_not_found(self, expense_service):
        """Test expense retrieval when expense doesn't exist."""
        expense_service.repository.get_by_id = Mock(return_value=None)
        
        with pytest.raises(NotFoundError) as exc_info:
            expense_service.get_expense(1)
        
        assert "Expense with ID 1 not found" in str(exc_info.value)
    
    def test_get_expense_invalid_id(self, expense_service):
        """Test expense retrieval with invalid ID."""
        with pytest.raises(ValidationError) as exc_info:
            expense_service.get_expense(-1)
        
        assert "Expense ID must be a positive integer" in str(exc_info.value)
    
    def test_get_expense_non_integer_id(self, expense_service):
        """Test expense retrieval with non-integer ID."""
        with pytest.raises(ValidationError) as exc_info:
            expense_service.get_expense("invalid")
        
        assert "Expense ID must be a positive integer" in str(exc_info.value)


class TestGetExpenses:
    """Test cases for expense list retrieval."""
    
    def test_get_expenses_success(self, expense_service, sample_expense):
        """Test successful expense list retrieval."""
        expenses = [sample_expense]
        total_count = 1
        
        expense_service.repository.get_all = Mock(return_value=(expenses, total_count))
        
        result_expenses, result_count = expense_service.get_expenses()
        
        assert result_expenses == expenses
        assert result_count == total_count
        expense_service.repository.get_all.assert_called_once()
    
    def test_get_expenses_with_pagination(self, expense_service, sample_expense):
        """Test expense list retrieval with pagination."""
        expenses = [sample_expense]
        total_count = 1
        
        expense_service.repository.get_all = Mock(return_value=(expenses, total_count))
        
        result_expenses, result_count = expense_service.get_expenses(page=2, per_page=10)
        
        # Verify pagination parameters were passed
        call_args = expense_service.repository.get_all.call_args
        assert call_args[1]['page'] == 2
        assert call_args[1]['per_page'] == 10
    
    def test_get_expenses_invalid_page(self, expense_service):
        """Test expense list retrieval with invalid page number."""
        with pytest.raises(ValidationError) as exc_info:
            expense_service.get_expenses(page=0)
        
        assert "Page must be a positive integer" in str(exc_info.value)
    
    def test_get_expenses_invalid_per_page(self, expense_service):
        """Test expense list retrieval with invalid per_page value."""
        with pytest.raises(ValidationError) as exc_info:
            expense_service.get_expenses(per_page=101)  # Over limit
        
        assert "Per page must be between 1 and 100" in str(exc_info.value)
    
    def test_get_expenses_invalid_sort_field(self, expense_service):
        """Test expense list retrieval with invalid sort field."""
        with pytest.raises(ValidationError) as exc_info:
            expense_service.get_expenses(sort_by='invalid_field')
        
        assert "Sort field must be one of" in str(exc_info.value)
    
    def test_get_expenses_invalid_sort_order(self, expense_service):
        """Test expense list retrieval with invalid sort order."""
        with pytest.raises(ValidationError) as exc_info:
            expense_service.get_expenses(sort_order='invalid')
        
        assert "Sort order must be 'asc' or 'desc'" in str(exc_info.value)
    
    def test_get_expenses_invalid_date_range(self, expense_service):
        """Test expense list retrieval with invalid date range."""
        start_date = datetime(2025, 2, 1)
        end_date = datetime(2025, 1, 1)  # End before start
        
        with pytest.raises(ValidationError) as exc_info:
            expense_service.get_expenses(start_date=start_date, end_date=end_date)
        
        assert "Start date must be before or equal to end date" in str(exc_info.value)


class TestUpdateExpense:
    """Test cases for expense updates."""
    
    def test_update_expense_success(self, expense_service, sample_expense):
        """Test successful expense update."""
        update_data = {'description': 'Updated description'}
        
        expense_service.repository.update = Mock(return_value=sample_expense)
        
        result = expense_service.update_expense(1, update_data)
        
        assert result == sample_expense
        expense_service.repository.update.assert_called_once()
    
    def test_update_expense_not_found(self, expense_service):
        """Test expense update when expense doesn't exist."""
        update_data = {'description': 'Updated description'}
        
        expense_service.repository.update = Mock(return_value=None)
        
        with pytest.raises(NotFoundError) as exc_info:
            expense_service.update_expense(1, update_data)
        
        assert "Expense with ID 1 not found" in str(exc_info.value)
    
    def test_update_expense_invalid_id(self, expense_service):
        """Test expense update with invalid ID."""
        update_data = {'description': 'Updated description'}
        
        with pytest.raises(ValidationError) as exc_info:
            expense_service.update_expense(-1, update_data)
        
        assert "Expense ID must be a positive integer" in str(exc_info.value)
    
    def test_update_expense_empty_data(self, expense_service):
        """Test expense update with empty update data."""
        with pytest.raises(ValidationError) as exc_info:
            expense_service.update_expense(1, {})
        
        assert "Validation failed" in str(exc_info.value)
    
    def test_update_expense_category_normalization(self, expense_service, sample_expense):
        """Test that category is normalized during update."""
        update_data = {'category': 'food and drinks'}
        
        expense_service.repository.update = Mock(return_value=sample_expense)
        
        result = expense_service.update_expense(1, update_data)
        
        # Verify that category is converted to title case
        call_args = expense_service.repository.update.call_args[0][1]
        assert call_args['category'] == 'Food And Drinks'


class TestDeleteExpense:
    """Test cases for expense deletion."""
    
    def test_delete_expense_success(self, expense_service):
        """Test successful expense deletion."""
        expense_service.repository.delete = Mock(return_value=True)
        
        result = expense_service.delete_expense(1)
        
        assert result is True
        expense_service.repository.delete.assert_called_once_with(1)
    
    def test_delete_expense_not_found(self, expense_service):
        """Test expense deletion when expense doesn't exist."""
        expense_service.repository.delete = Mock(return_value=False)
        
        with pytest.raises(NotFoundError) as exc_info:
            expense_service.delete_expense(1)
        
        assert "Expense with ID 1 not found" in str(exc_info.value)
    
    def test_delete_expense_invalid_id(self, expense_service):
        """Test expense deletion with invalid ID."""
        with pytest.raises(ValidationError) as exc_info:
            expense_service.delete_expense(-1)
        
        assert "Expense ID must be a positive integer" in str(exc_info.value)


class TestGetCategories:
    """Test cases for category retrieval."""
    
    def test_get_categories_success(self, expense_service):
        """Test successful category retrieval."""
        categories = ['Food', 'Transport', 'Entertainment']
        
        expense_service.repository.get_categories = Mock(return_value=categories)
        
        result = expense_service.get_categories()
        
        assert 'Uncategorized' in result
        assert all(cat in result for cat in categories)
        assert result == sorted(result)  # Should be sorted
    
    def test_get_categories_with_uncategorized(self, expense_service):
        """Test category retrieval when Uncategorized already exists."""
        categories = ['Food', 'Uncategorized', 'Transport']
        
        expense_service.repository.get_categories = Mock(return_value=categories)
        
        result = expense_service.get_categories()
        
        # Should not duplicate Uncategorized
        assert result.count('Uncategorized') == 1
        assert result == sorted(result)
    
    def test_get_categories_empty(self, expense_service):
        """Test category retrieval when no categories exist."""
        expense_service.repository.get_categories = Mock(return_value=[])
        
        result = expense_service.get_categories()
        
        # Should return empty list when no expenses exist
        assert result == []


class TestGetExpenseSummary:
    """Test cases for expense summary."""
    
    def test_get_expense_summary_success(self, expense_service):
        """Test successful expense summary retrieval."""
        summary_data = {
            'total_amount': 150.755,  # Will be rounded
            'expense_count': 5,
            'date_range': {'start': None, 'end': None},
            'categories': [
                {'category': 'Food', 'amount': 85.255, 'count': 3},
                {'category': 'Transport', 'amount': 65.50, 'count': 2}
            ]
        }
        
        expense_service.repository.get_summary = Mock(return_value=summary_data)
        
        result = expense_service.get_expense_summary()
        
        # Verify amounts are rounded to 2 decimal places
        assert result['total_amount'] == 150.76
        assert result['categories'][0]['amount'] == 85.26
        assert result['categories'][1]['amount'] == 65.50
    
    def test_get_expense_summary_with_date_range(self, expense_service):
        """Test expense summary with date range."""
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 31)
        
        expense_service.repository.get_summary = Mock(return_value={
            'total_amount': 100.0,
            'expense_count': 2,
            'date_range': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'categories': []
        })
        
        result = expense_service.get_expense_summary(start_date, end_date)
        
        expense_service.repository.get_summary.assert_called_once_with(start_date, end_date)
    
    def test_get_expense_summary_invalid_date_range(self, expense_service):
        """Test expense summary with invalid date range."""
        start_date = datetime(2025, 2, 1)
        end_date = datetime(2025, 1, 1)  # End before start
        
        with pytest.raises(ValidationError) as exc_info:
            expense_service.get_expense_summary(start_date, end_date)
        
        assert "Start date must be before or equal to end date" in str(exc_info.value)


class TestBusinessRules:
    """Test cases for business rule application."""
    
    def test_apply_creation_business_rules(self, expense_service):
        """Test business rules applied during creation."""
        expense_data = {
            'amount': '25.555',  # Should be rounded
            'description': '  Coffee and pastry  ',  # Should be trimmed
            'category': '  food  '  # Should be trimmed and title-cased
        }
        
        result = expense_service._apply_creation_business_rules(expense_data)
        
        assert result['amount'] == Decimal('25.56')
        assert result['description'] == 'Coffee and pastry'
        assert result['category'] == 'Food'
    
    def test_apply_update_business_rules(self, expense_service):
        """Test business rules applied during updates."""
        expense_data = {
            'amount': '30.999',  # Should be rounded
            'description': '  Updated description  ',  # Should be trimmed
            'category': '  transport  '  # Should be trimmed and title-cased
        }
        
        result = expense_service._apply_update_business_rules(expense_data)
        
        assert result['amount'] == Decimal('31.00')
        assert result['description'] == 'Updated description'
        assert result['category'] == 'Transport'
    
    def test_apply_summary_business_rules(self, expense_service):
        """Test business rules applied to summary data."""
        summary_data = {
            'total_amount': 150.755,
            'categories': [
                {'category': 'Food', 'amount': 85.255, 'count': 3}
            ]
        }
        
        result = expense_service._apply_summary_business_rules(summary_data)
        
        assert result['total_amount'] == 150.76
        assert result['categories'][0]['amount'] == 85.26