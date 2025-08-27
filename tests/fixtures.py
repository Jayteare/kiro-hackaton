"""
Test fixtures and factories for consistent test data generation.

This module provides reusable test data factories and fixtures to ensure
consistent test data across all test modules.
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from app import create_app, db
from app.models.expense import Expense


class ExpenseFactory:
    """Factory for creating expense test data."""
    
    @staticmethod
    def build_expense_data(**kwargs) -> Dict[str, Any]:
        """Build expense data dictionary with default values."""
        defaults = {
            'amount': '25.50',
            'description': 'Test expense',
            'category': 'Food',
            'date': datetime.utcnow().isoformat()
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def build_multiple_expenses(count: int = 5) -> List[Dict[str, Any]]:
        """Build multiple expense data dictionaries."""
        base_date = datetime(2025, 1, 1)
        categories = ['Food', 'Transport', 'Entertainment', 'Utilities', 'Shopping']
        descriptions = [
            'Coffee and pastry',
            'Bus ticket',
            'Movie tickets',
            'Electricity bill',
            'Groceries'
        ]
        amounts = ['25.50', '15.00', '30.00', '75.00', '120.00']
        
        expenses = []
        for i in range(count):
            expense_data = {
                'amount': amounts[i % len(amounts)],
                'description': descriptions[i % len(descriptions)],
                'category': categories[i % len(categories)],
                'date': (base_date + timedelta(days=i)).isoformat()
            }
            expenses.append(expense_data)
        
        return expenses
    
    @staticmethod
    def create_expense_in_db(session, **kwargs) -> Expense:
        """Create and persist an expense in the database."""
        defaults = {
            'amount': Decimal('25.50'),
            'description': 'Test expense',
            'category': 'Food',
            'date': datetime.utcnow()
        }
        defaults.update(kwargs)
        
        expense = Expense(**defaults)
        session.add(expense)
        session.commit()
        return expense
    
    @staticmethod
    def create_multiple_expenses_in_db(session, count: int = 5) -> List[Expense]:
        """Create and persist multiple expenses in the database."""
        base_date = datetime(2025, 1, 1)
        categories = ['Food', 'Transport', 'Entertainment', 'Utilities', 'Shopping']
        descriptions = [
            'Coffee and pastry',
            'Bus ticket',
            'Movie tickets',
            'Electricity bill',
            'Groceries'
        ]
        amounts = [Decimal('25.50'), Decimal('15.00'), Decimal('30.00'), 
                  Decimal('75.00'), Decimal('120.00')]
        
        expenses = []
        for i in range(count):
            expense = Expense(
                amount=amounts[i % len(amounts)],
                description=descriptions[i % len(descriptions)],
                category=categories[i % len(categories)],
                date=base_date + timedelta(days=i)
            )
            session.add(expense)
            expenses.append(expense)
        
        session.commit()
        return expenses


class ValidationTestData:
    """Test data for validation scenarios."""
    
    @staticmethod
    def invalid_amounts() -> List[str]:
        """Return list of invalid amount values."""
        return [
            '-10.00',      # Negative
            '0.00',        # Zero
            'invalid',     # Non-numeric
            '',            # Empty
            '10.999',      # Too many decimals (should be rounded)
        ]
    
    @staticmethod
    def invalid_descriptions() -> List[str]:
        """Return list of invalid description values."""
        return [
            '',            # Empty
            '   ',         # Whitespace only
            'x' * 256,     # Too long (exceeds 255 chars)
        ]
    
    @staticmethod
    def invalid_categories() -> List[str]:
        """Return list of invalid category values."""
        return [
            'x' * 101,     # Too long (exceeds 100 chars)
        ]
    
    @staticmethod
    def valid_edge_cases() -> List[Dict[str, Any]]:
        """Return list of valid edge case data."""
        return [
            {
                'amount': '0.01',
                'description': 'Minimum amount',
                'category': 'Test'
            },
            {
                'amount': '999999.99',
                'description': 'Maximum amount',
                'category': 'Test'
            },
            {
                'amount': '25.50',
                'description': 'Unicode test ☕ 🥐',
                'category': 'Food & Drinks'
            },
            {
                'amount': '25.50',
                'description': 'x' * 255,  # Maximum length description
                'category': 'y' * 100      # Maximum length category
            }
        ]


class APITestData:
    """Test data for API endpoint testing."""
    
    @staticmethod
    def pagination_test_cases() -> List[Dict[str, Any]]:
        """Return test cases for pagination testing."""
        return [
            {'page': 1, 'per_page': 5, 'expected_items': 5},
            {'page': 2, 'per_page': 5, 'expected_items': 5},
            {'page': 3, 'per_page': 5, 'expected_items': 2},  # Last page with fewer items
            {'page': 1, 'per_page': 20, 'expected_items': 12}, # All items on one page
        ]
    
    @staticmethod
    def filter_test_cases() -> List[Dict[str, Any]]:
        """Return test cases for filtering testing."""
        return [
            {
                'filter': {'category': 'Food'},
                'expected_count': 3,
                'description': 'Filter by Food category'
            },
            {
                'filter': {'category': 'Transport'},
                'expected_count': 2,
                'description': 'Filter by Transport category'
            },
            {
                'filter': {'start_date': '2025-01-02T00:00:00Z'},
                'expected_count': 4,
                'description': 'Filter by start date'
            },
            {
                'filter': {'end_date': '2025-01-03T23:59:59Z'},
                'expected_count': 3,
                'description': 'Filter by end date'
            }
        ]
    
    @staticmethod
    def sorting_test_cases() -> List[Dict[str, Any]]:
        """Return test cases for sorting testing."""
        return [
            {
                'sort_by': 'amount',
                'sort_order': 'asc',
                'expected_first_amount': '15.00',
                'expected_last_amount': '120.00'
            },
            {
                'sort_by': 'amount',
                'sort_order': 'desc',
                'expected_first_amount': '120.00',
                'expected_last_amount': '15.00'
            },
            {
                'sort_by': 'date',
                'sort_order': 'asc',
                'expected_order': 'chronological'
            },
            {
                'sort_by': 'category',
                'sort_order': 'asc',
                'expected_order': 'alphabetical'
            }
        ]


@pytest.fixture(scope='function')
def test_app():
    """Create a test application instance."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def test_client(test_app):
    """Create a test client."""
    return test_app.test_client()


@pytest.fixture(scope='function')
def test_db_session(test_app):
    """Create a test database session."""
    with test_app.app_context():
        yield db.session


@pytest.fixture(scope='function')
def sample_expense_data():
    """Provide sample expense data for testing."""
    return ExpenseFactory.build_expense_data()


@pytest.fixture(scope='function')
def multiple_expense_data():
    """Provide multiple expense data for testing."""
    return ExpenseFactory.build_multiple_expenses(12)


@pytest.fixture(scope='function')
def created_expenses(client, multiple_expense_data):
    """Create multiple expenses in the test database via API."""
    created = []
    for expense_data in multiple_expense_data:
        response = client.post(
            '/api/expenses',
            json=expense_data,
            content_type='application/json'
        )
        assert response.status_code == 201
        created.append(response.get_json())
    return created


@pytest.fixture(scope='function')
def expense_factory():
    """Provide ExpenseFactory instance."""
    return ExpenseFactory


@pytest.fixture(scope='function')
def validation_data():
    """Provide ValidationTestData instance."""
    return ValidationTestData


@pytest.fixture(scope='function')
def api_test_data():
    """Provide APITestData instance."""
    return APITestData


@pytest.fixture(scope='function')
def performance_dataset(client):
    """Create a large dataset for performance testing."""
    # Create 50 expenses for performance testing
    expenses_data = []
    base_date = datetime(2025, 1, 1)
    categories = ['Food', 'Transport', 'Entertainment', 'Utilities', 'Shopping', 'Health']
    descriptions = [
        'Coffee shop visit', 'Bus fare', 'Movie tickets', 'Electric bill', 
        'Grocery shopping', 'Doctor visit', 'Gas station', 'Restaurant meal',
        'Online subscription', 'Pharmacy purchase'
    ]
    
    for i in range(50):
        expense_data = {
            'amount': f'{(i % 20 + 1) * 5}.{i % 100:02d}',
            'description': descriptions[i % len(descriptions)],
            'category': categories[i % len(categories)],
            'date': (base_date + timedelta(days=i % 30, hours=i % 24)).isoformat()
        }
        expenses_data.append(expense_data)
    
    # Batch create expenses
    created_expenses = []
    for expense_data in expenses_data:
        response = client.post('/api/expenses', json=expense_data)
        assert response.status_code == 201
        created_expenses.append(response.get_json())
    
    return created_expenses


@pytest.fixture(scope='function')
def edge_case_expenses(client):
    """Create expenses with edge case values for testing."""
    edge_cases = [
        {
            'amount': '0.01',
            'description': 'Minimum amount test',
            'category': 'Test',
            'date': '2025-01-01T00:00:00Z'
        },
        {
            'amount': '999999.99',
            'description': 'Maximum amount test',
            'category': 'Test',
            'date': '2025-12-31T23:59:59Z'
        },
        {
            'amount': '25.50',
            'description': 'Unicode test ☕ 🥐 café',
            'category': 'Food & Drinks',
            'date': '2025-06-15T12:30:00Z'
        },
        {
            'amount': '100.00',
            'description': 'x' * 255,  # Maximum length description
            'category': 'y' * 100,     # Maximum length category
            'date': '2025-03-15T09:45:00Z'
        }
    ]
    
    created_expenses = []
    for expense_data in edge_cases:
        response = client.post('/api/expenses', json=expense_data)
        assert response.status_code == 201
        created_expenses.append(response.get_json())
    
    return created_expenses


@pytest.fixture(scope='function')
def date_range_expenses(client):
    """Create expenses across different date ranges for filtering tests."""
    base_date = datetime(2025, 1, 1)
    expenses_data = []
    
    # Create expenses across 6 months
    for month in range(6):
        for day in [1, 15]:  # Two expenses per month
            expense_date = base_date.replace(month=month + 1, day=day)
            expense_data = {
                'amount': f'{(month + 1) * 10}.00',
                'description': f'Month {month + 1} expense',
                'category': 'Monthly',
                'date': expense_date.isoformat()
            }
            expenses_data.append(expense_data)
    
    created_expenses = []
    for expense_data in expenses_data:
        response = client.post('/api/expenses', json=expense_data)
        assert response.status_code == 201
        created_expenses.append(response.get_json())
    
    return created_expenses