"""
Integration tests for expense API endpoints.
"""
import json
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from app import create_app, db
from app.models.expense import Expense


@pytest.fixture
def app():
    """Create test application."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_expense_data():
    """Sample expense data for testing."""
    return {
        'amount': '25.50',
        'description': 'Coffee and pastry',
        'category': 'Food',
        'date': '2025-01-15T10:30:00Z'
    }


class TestExpenseCreation:
    """Test expense creation endpoint."""
    
    def test_create_expense_success(self, client, sample_expense_data):
        """Test successful expense creation."""
        response = client.post(
            '/api/expenses',
            data=json.dumps(sample_expense_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        # Verify response structure
        assert 'id' in data
        assert data['amount'] == '25.50'
        assert data['description'] == 'Coffee and pastry'
        assert data['category'] == 'Food'
        assert 'date' in data
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_create_expense_minimal_data(self, client):
        """Test expense creation with minimal required data."""
        minimal_data = {
            'amount': '10.00',
            'description': 'Test expense'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(minimal_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        assert data['amount'] == '10.00'
        assert data['description'] == 'Test expense'
        assert data['category'] == 'Uncategorized'  # Default category
        assert 'date' in data  # Should have default date
    
    def test_create_expense_missing_amount(self, client):
        """Test expense creation with missing amount."""
        invalid_data = {
            'description': 'Test expense'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_create_expense_missing_description(self, client):
        """Test expense creation with missing description."""
        invalid_data = {
            'amount': '25.50'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_create_expense_negative_amount(self, client):
        """Test expense creation with negative amount."""
        invalid_data = {
            'amount': '-10.00',
            'description': 'Test expense'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_create_expense_zero_amount(self, client):
        """Test expense creation with zero amount."""
        invalid_data = {
            'amount': '0.00',
            'description': 'Test expense'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_create_expense_invalid_amount_format(self, client):
        """Test expense creation with invalid amount format."""
        invalid_data = {
            'amount': 'not_a_number',
            'description': 'Test expense'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_create_expense_empty_description(self, client):
        """Test expense creation with empty description."""
        invalid_data = {
            'amount': '25.50',
            'description': ''
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_create_expense_whitespace_description(self, client):
        """Test expense creation with whitespace-only description."""
        invalid_data = {
            'amount': '25.50',
            'description': '   '
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_create_expense_long_description(self, client):
        """Test expense creation with description too long."""
        invalid_data = {
            'amount': '25.50',
            'description': 'x' * 256  # Exceeds 255 character limit
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_create_expense_empty_category(self, client):
        """Test expense creation with empty category defaults to Uncategorized."""
        data = {
            'amount': '25.50',
            'description': 'Test expense',
            'category': ''
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['category'] == 'Uncategorized'
    
    def test_create_expense_whitespace_category(self, client):
        """Test expense creation with whitespace category defaults to Uncategorized."""
        data = {
            'amount': '25.50',
            'description': 'Test expense',
            'category': '   '
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['category'] == 'Uncategorized'
    
    def test_create_expense_invalid_json(self, client):
        """Test expense creation with invalid JSON."""
        response = client.post(
            '/api/expenses',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_JSON'
    
    def test_create_expense_no_content_type(self, client, sample_expense_data):
        """Test expense creation without JSON content type."""
        response = client.post(
            '/api/expenses',
            data=json.dumps(sample_expense_data)
            # No content_type specified
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_CONTENT_TYPE'
    
    def test_create_expense_wrong_content_type(self, client, sample_expense_data):
        """Test expense creation with wrong content type."""
        response = client.post(
            '/api/expenses',
            data=json.dumps(sample_expense_data),
            content_type='text/plain'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_CONTENT_TYPE'
    
    def test_create_expense_null_json(self, client):
        """Test expense creation with null JSON."""
        response = client.post(
            '/api/expenses',
            data='null',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_JSON'
    
    def test_create_expense_database_persistence(self, client, sample_expense_data, app):
        """Test that created expense is persisted in database."""
        response = client.post(
            '/api/expenses',
            data=json.dumps(sample_expense_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        expense_id = response_data['id']
        
        # Verify expense exists in database
        with app.app_context():
            expense = db.session.get(Expense, expense_id)
            assert expense is not None
            assert str(expense.amount) == '25.50'
            assert expense.description == 'Coffee and pastry'
            assert expense.category == 'Food'
    
    def test_create_expense_amount_precision(self, client):
        """Test expense creation with various amount precisions."""
        test_cases = [
            ('10', '10.00'),
            ('10.5', '10.50'),
            ('10.50', '10.50'),
            ('10.123', '10.12'),  # Should round to 2 decimal places
            ('10.999', '11.00'),  # Should round up
        ]
        
        for input_amount, expected_amount in test_cases:
            data = {
                'amount': input_amount,
                'description': f'Test expense {input_amount}'
            }
            
            response = client.post(
                '/api/expenses',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 201
            response_data = json.loads(response.data)
            assert response_data['amount'] == expected_amount
    
    def test_create_expense_date_formats(self, client):
        """Test expense creation with various date formats."""
        # Test with ISO format
        data = {
            'amount': '25.50',
            'description': 'Test expense',
            'date': '2025-01-15T10:30:00Z'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert '2025-01-15' in response_data['date']
    
    def test_create_expense_ignores_readonly_fields(self, client):
        """Test that readonly fields are ignored during creation."""
        data = {
            'amount': '25.50',
            'description': 'Test expense',
            'id': 999,  # Should be ignored
            'created_at': '2020-01-01T00:00:00Z',  # Should be ignored
            'updated_at': '2020-01-01T00:00:00Z'   # Should be ignored
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        
        # ID should be auto-generated, not 999
        assert response_data['id'] != 999
        
        # Timestamps should be current, not from 2020
        assert '2020' not in response_data['created_at']
        assert '2020' not in response_data['updated_at']


class TestExpenseRetrieval:
    """Test expense retrieval endpoints."""
    
    def create_sample_expenses(self, client):
        """Helper method to create sample expenses for testing."""
        expenses_data = [
            {
                'amount': '25.50',
                'description': 'Coffee and pastry',
                'category': 'Food',
                'date': '2025-01-15T10:30:00Z'
            },
            {
                'amount': '15.00',
                'description': 'Bus ticket',
                'category': 'Transport',
                'date': '2025-01-14T08:00:00Z'
            },
            {
                'amount': '100.00',
                'description': 'Groceries',
                'category': 'Food',
                'date': '2025-01-13T18:00:00Z'
            },
            {
                'amount': '50.00',
                'description': 'Gas bill',
                'category': 'Utilities',
                'date': '2025-01-12T12:00:00Z'
            },
            {
                'amount': '30.00',
                'description': 'Movie tickets',
                'category': 'Entertainment',
                'date': '2025-01-11T20:00:00Z'
            }
        ]
        
        created_expenses = []
        for expense_data in expenses_data:
            response = client.post(
                '/api/expenses',
                data=json.dumps(expense_data),
                content_type='application/json'
            )
            assert response.status_code == 201
            created_expenses.append(json.loads(response.data))
        
        return created_expenses
    
    def test_get_all_expenses_empty(self, client):
        """Test getting expenses when none exist."""
        response = client.get('/api/expenses')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'expenses' in data
        assert 'pagination' in data
        assert data['expenses'] == []
        assert data['pagination']['total_count'] == 0
        assert data['pagination']['total_pages'] == 0
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 20
        assert data['pagination']['has_next'] is False
        assert data['pagination']['has_prev'] is False
    
    def test_get_all_expenses_success(self, client):
        """Test successful retrieval of all expenses."""
        # Create sample expenses
        created_expenses = self.create_sample_expenses(client)
        
        response = client.get('/api/expenses')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'expenses' in data
        assert 'pagination' in data
        assert len(data['expenses']) == 5
        assert data['pagination']['total_count'] == 5
        assert data['pagination']['total_pages'] == 1
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 20
        assert data['pagination']['has_next'] is False
        assert data['pagination']['has_prev'] is False
        
        # Verify expenses are returned in reverse chronological order (newest first)
        expenses = data['expenses']
        assert expenses[0]['description'] == 'Coffee and pastry'  # 2025-01-15
        assert expenses[1]['description'] == 'Bus ticket'         # 2025-01-14
        assert expenses[2]['description'] == 'Groceries'          # 2025-01-13
        assert expenses[3]['description'] == 'Gas bill'           # 2025-01-12
        assert expenses[4]['description'] == 'Movie tickets'      # 2025-01-11
    
    def test_get_expenses_pagination(self, client):
        """Test expense retrieval with pagination."""
        # Create sample expenses
        self.create_sample_expenses(client)
        
        # Test first page with 2 items per page
        response = client.get('/api/expenses?page=1&per_page=2')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['expenses']) == 2
        assert data['pagination']['total_count'] == 5
        assert data['pagination']['total_pages'] == 3
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 2
        assert data['pagination']['has_next'] is True
        assert data['pagination']['has_prev'] is False
        
        # Test second page
        response = client.get('/api/expenses?page=2&per_page=2')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['expenses']) == 2
        assert data['pagination']['page'] == 2
        assert data['pagination']['has_next'] is True
        assert data['pagination']['has_prev'] is True
        
        # Test last page
        response = client.get('/api/expenses?page=3&per_page=2')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['expenses']) == 1  # Only 1 item on last page
        assert data['pagination']['page'] == 3
        assert data['pagination']['has_next'] is False
        assert data['pagination']['has_prev'] is True
    
    def test_get_expenses_category_filter(self, client):
        """Test expense retrieval with category filtering."""
        # Create sample expenses
        self.create_sample_expenses(client)
        
        # Filter by Food category
        response = client.get('/api/expenses?category=Food')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['expenses']) == 2  # Coffee and Groceries
        assert data['pagination']['total_count'] == 2
        
        for expense in data['expenses']:
            assert expense['category'] == 'Food'
        
        # Filter by Transport category
        response = client.get('/api/expenses?category=Transport')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['expenses']) == 1  # Bus ticket
        assert data['expenses'][0]['category'] == 'Transport'
        assert data['expenses'][0]['description'] == 'Bus ticket'
        
        # Filter by non-existent category
        response = client.get('/api/expenses?category=NonExistent')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['expenses']) == 0
        assert data['pagination']['total_count'] == 0
    
    def test_get_expenses_date_filter(self, client):
        """Test expense retrieval with date filtering."""
        # Create sample expenses
        self.create_sample_expenses(client)
        
        # Filter by start date
        response = client.get('/api/expenses?start_date=2025-01-14T00:00:00Z')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['expenses']) == 2  # Coffee and Bus ticket (14th and 15th)
        
        # Filter by end date
        response = client.get('/api/expenses?end_date=2025-01-12T23:59:59Z')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['expenses']) == 2  # Gas bill and Movie tickets (11th and 12th)
        
        # Filter by date range
        response = client.get('/api/expenses?start_date=2025-01-12T00:00:00Z&end_date=2025-01-14T23:59:59Z')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['expenses']) == 3  # Gas bill, Groceries, Bus ticket (12th, 13th, 14th)
    
    def test_get_expenses_sorting(self, client):
        """Test expense retrieval with different sorting options."""
        # Create sample expenses
        self.create_sample_expenses(client)
        
        # Sort by amount ascending
        response = client.get('/api/expenses?sort_by=amount&sort_order=asc')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        expenses = data['expenses']
        amounts = [float(expense['amount']) for expense in expenses]
        assert amounts == sorted(amounts)  # Should be in ascending order
        assert expenses[0]['amount'] == '15.00'  # Bus ticket (lowest)
        assert expenses[-1]['amount'] == '100.00'  # Groceries (highest)
        
        # Sort by amount descending
        response = client.get('/api/expenses?sort_by=amount&sort_order=desc')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        expenses = data['expenses']
        amounts = [float(expense['amount']) for expense in expenses]
        assert amounts == sorted(amounts, reverse=True)  # Should be in descending order
        
        # Sort by category
        response = client.get('/api/expenses?sort_by=category&sort_order=asc')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        expenses = data['expenses']
        categories = [expense['category'] for expense in expenses]
        assert categories == sorted(categories)  # Should be alphabetically sorted
    
    def test_get_expenses_invalid_pagination(self, client):
        """Test expense retrieval with invalid pagination parameters."""
        # Invalid page number
        response = client.get('/api/expenses?page=0')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Invalid per_page
        response = client.get('/api/expenses?per_page=0')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        
        # Per_page too large
        response = client.get('/api/expenses?per_page=101')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        
        # Non-numeric page
        response = client.get('/api/expenses?page=invalid')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_expenses_invalid_sort(self, client):
        """Test expense retrieval with invalid sort parameters."""
        # Invalid sort field
        response = client.get('/api/expenses?sort_by=invalid_field')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Invalid sort order
        response = client.get('/api/expenses?sort_order=invalid')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_get_expenses_invalid_date(self, client):
        """Test expense retrieval with invalid date parameters."""
        # Invalid date format
        response = client.get('/api/expenses?start_date=invalid-date')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_PARAMETERS'
        
        # Invalid end date
        response = client.get('/api/expenses?end_date=not-a-date')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_single_expense_success(self, client):
        """Test successful retrieval of a single expense."""
        # Create a sample expense
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee and pastry',
            'category': 'Food',
            'date': '2025-01-15T10:30:00Z'
        }
        
        create_response = client.post(
            '/api/expenses',
            data=json.dumps(expense_data),
            content_type='application/json'
        )
        
        assert create_response.status_code == 201
        created_expense = json.loads(create_response.data)
        expense_id = created_expense['id']
        
        # Retrieve the expense
        response = client.get(f'/api/expenses/{expense_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['id'] == expense_id
        assert data['amount'] == '25.50'
        assert data['description'] == 'Coffee and pastry'
        assert data['category'] == 'Food'
        assert 'date' in data
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_get_single_expense_not_found(self, client):
        """Test retrieval of non-existent expense."""
        response = client.get('/api/expenses/999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        
        assert 'error' in data
        assert data['error']['code'] == 'NOT_FOUND'
        assert 'not found' in data['error']['message'].lower()
    
    def test_get_single_expense_invalid_id(self, client):
        """Test retrieval with invalid expense ID."""
        # Non-numeric ID
        response = client.get('/api/expenses/invalid')
        
        # Flask will return 404 for invalid route parameter
        assert response.status_code == 404
        
        # Zero ID
        response = client.get('/api/expenses/0')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Negative ID (Flask treats negative numbers as invalid route parameters)
        response = client.get('/api/expenses/-1')
        
        # Flask returns 404 for negative integers in route parameters
        assert response.status_code == 404
    
    def test_get_expenses_combined_filters(self, client):
        """Test expense retrieval with multiple filters combined."""
        # Create sample expenses
        self.create_sample_expenses(client)
        
        # Combine category and date filters
        response = client.get('/api/expenses?category=Food&start_date=2025-01-14T00:00:00Z')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['expenses']) == 1  # Only Coffee (Food category after 14th)
        assert data['expenses'][0]['description'] == 'Coffee and pastry'
        assert data['expenses'][0]['category'] == 'Food'
        
        # Combine pagination with filters
        response = client.get('/api/expenses?category=Food&page=1&per_page=1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['expenses']) == 1
        assert data['pagination']['total_count'] == 2  # Total Food items
        assert data['pagination']['has_next'] is True
    
    def test_get_expenses_response_structure(self, client):
        """Test that expense retrieval response has correct structure."""
        # Create a sample expense
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee and pastry',
            'category': 'Food'
        }
        
        client.post(
            '/api/expenses',
            data=json.dumps(expense_data),
            content_type='application/json'
        )
        
        response = client.get('/api/expenses')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check top-level structure
        assert 'expenses' in data
        assert 'pagination' in data
        assert isinstance(data['expenses'], list)
        assert isinstance(data['pagination'], dict)
        
        # Check pagination structure
        pagination = data['pagination']
        required_pagination_fields = ['page', 'per_page', 'total_count', 'total_pages', 'has_next', 'has_prev']
        for field in required_pagination_fields:
            assert field in pagination
        
        # Check expense structure
        if data['expenses']:
            expense = data['expenses'][0]
            required_expense_fields = ['id', 'amount', 'description', 'category', 'date', 'created_at', 'updated_at']
            for field in required_expense_fields:
                assert field in expense


class TestExpenseUpdate:
    """Test expense update endpoint."""
    
    def create_sample_expense(self, client):
        """Helper method to create a sample expense for testing."""
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee and pastry',
            'category': 'Food',
            'date': '2025-01-15T10:30:00Z'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(expense_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        return json.loads(response.data)
    
    def test_update_expense_success(self, client):
        """Test successful expense update."""
        # Create expense
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        # Update expense
        update_data = {
            'amount': '30.00',
            'description': 'Updated coffee and pastry',
            'category': 'Updated Food'
        }
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['id'] == expense_id
        assert data['amount'] == '30.00'
        assert data['description'] == 'Updated coffee and pastry'
        assert data['category'] == 'Updated Food'
        assert data['date'] == expense['date']  # Date should remain unchanged
        assert 'updated_at' in data
        # Updated timestamp should be different from created timestamp
        assert data['updated_at'] != data['created_at']
    
    def test_update_expense_partial(self, client):
        """Test partial expense update (only some fields)."""
        # Create expense
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        # Update only amount
        update_data = {
            'amount': '35.75'
        }
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['id'] == expense_id
        assert data['amount'] == '35.75'
        # Other fields should remain unchanged
        assert data['description'] == expense['description']
        assert data['category'] == expense['category']
        assert data['date'] == expense['date']
    
    def test_update_expense_not_found(self, client):
        """Test updating non-existent expense."""
        update_data = {
            'amount': '30.00',
            'description': 'Updated description'
        }
        
        response = client.put(
            '/api/expenses/999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        
        assert 'error' in data
        assert data['error']['code'] == 'NOT_FOUND'
        assert 'not found' in data['error']['message'].lower()
    
    def test_update_expense_invalid_id(self, client):
        """Test updating with invalid expense ID."""
        update_data = {
            'amount': '30.00'
        }
        
        # Zero ID
        response = client.put(
            '/api/expenses/0',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Non-numeric ID returns 404 from Flask routing
        response = client.put(
            '/api/expenses/invalid',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    def test_update_expense_invalid_amount(self, client):
        """Test updating with invalid amount values."""
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        # Negative amount
        update_data = {'amount': '-10.00'}
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Zero amount
        update_data = {'amount': '0.00'}
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Invalid amount format
        update_data = {'amount': 'not_a_number'}
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_update_expense_invalid_description(self, client):
        """Test updating with invalid description values."""
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        # Empty description
        update_data = {'description': ''}
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Whitespace-only description
        update_data = {'description': '   '}
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Description too long
        update_data = {'description': 'x' * 256}
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_update_expense_empty_category(self, client):
        """Test updating with empty category defaults to Uncategorized."""
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        # Empty category
        update_data = {'category': ''}
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['category'] == 'Uncategorized'
        
        # Whitespace category
        update_data = {'category': '   '}
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['category'] == 'Uncategorized'
    
    def test_update_expense_invalid_json(self, client):
        """Test updating with invalid JSON."""
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_JSON'
    
    def test_update_expense_no_content_type(self, client):
        """Test updating without JSON content type."""
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        update_data = {'amount': '30.00'}
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data)
            # No content_type specified
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_CONTENT_TYPE'
    
    def test_update_expense_wrong_content_type(self, client):
        """Test updating with wrong content type."""
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        update_data = {'amount': '30.00'}
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data),
            content_type='text/plain'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_CONTENT_TYPE'
    
    def test_update_expense_null_json(self, client):
        """Test updating with null JSON."""
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data='null',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_JSON'
    
    def test_update_expense_empty_payload(self, client):
        """Test updating with empty payload."""
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data='{}',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
        # Should require at least one field for update
    
    def test_update_expense_database_persistence(self, client, app):
        """Test that updated expense is persisted in database."""
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        update_data = {
            'amount': '40.00',
            'description': 'Updated description'
        }
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Verify expense is updated in database
        with app.app_context():
            from app.models.expense import Expense
            updated_expense = db.session.get(Expense, expense_id)
            assert updated_expense is not None
            assert str(updated_expense.amount) == '40.00'
            assert updated_expense.description == 'Updated description'
            # Category should remain unchanged
            assert updated_expense.category == expense['category']
    
    def test_update_expense_amount_precision(self, client):
        """Test expense update with various amount precisions."""
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        test_cases = [
            ('10', '10.00'),
            ('10.5', '10.50'),
            ('10.50', '10.50'),
            ('10.123', '10.12'),  # Should round to 2 decimal places
            ('10.999', '11.00'),  # Should round up
        ]
        
        for input_amount, expected_amount in test_cases:
            update_data = {'amount': input_amount}
            
            response = client.put(
                f'/api/expenses/{expense_id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['amount'] == expected_amount
    
    def test_update_expense_date_format(self, client):
        """Test expense update with date field."""
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        # Update with new date
        update_data = {
            'date': '2025-02-01T15:00:00Z'
        }
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert '2025-02-01' in data['date']
    
    def test_update_expense_ignores_readonly_fields(self, client):
        """Test that readonly fields are ignored during update."""
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        original_created_at = expense['created_at']
        
        # Try to update readonly fields
        update_data = {
            'amount': '30.00',
            'id': 999,  # Should be ignored
            'created_at': '2020-01-01T00:00:00Z',  # Should be ignored
        }
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # ID should remain unchanged
        assert data['id'] == expense_id
        
        # Created timestamp should remain unchanged
        assert data['created_at'] == original_created_at
        
        # Amount should be updated
        assert data['amount'] == '30.00'
    
    def test_update_expense_multiple_fields(self, client):
        """Test updating multiple fields at once."""
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        update_data = {
            'amount': '45.75',
            'description': 'Completely updated expense',
            'category': 'New Category',
            'date': '2025-03-01T12:00:00Z'
        }
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['id'] == expense_id
        assert data['amount'] == '45.75'
        assert data['description'] == 'Completely updated expense'
        assert data['category'] == 'New Category'
        assert '2025-03-01' in data['date']
        assert data['updated_at'] != data['created_at']


class TestExpenseDeletion:
    """Test expense deletion endpoint."""
    
    def create_sample_expense(self, client):
        """Helper method to create a sample expense for testing."""
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee and pastry',
            'category': 'Food',
            'date': '2025-01-15T10:30:00Z'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(expense_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        return json.loads(response.data)
    
    def test_delete_expense_success(self, client):
        """Test successful expense deletion."""
        # Create expense
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        # Delete expense
        response = client.delete(f'/api/expenses/{expense_id}')
        
        assert response.status_code == 204
        assert response.data == b''  # No content in response body
        
        # Verify expense is deleted by trying to retrieve it
        get_response = client.get(f'/api/expenses/{expense_id}')
        assert get_response.status_code == 404
    
    def test_delete_expense_not_found(self, client):
        """Test deleting non-existent expense."""
        response = client.delete('/api/expenses/999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        
        assert 'error' in data
        assert data['error']['code'] == 'NOT_FOUND'
        assert 'not found' in data['error']['message'].lower()
    
    def test_delete_expense_invalid_id(self, client):
        """Test deleting with invalid expense ID."""
        # Zero ID
        response = client.delete('/api/expenses/0')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Non-numeric ID returns 404 from Flask routing
        response = client.delete('/api/expenses/invalid')
        
        assert response.status_code == 404
        
        # Negative ID (Flask treats as invalid route parameter)
        response = client.delete('/api/expenses/-1')
        
        assert response.status_code == 404
    
    def test_delete_expense_database_persistence(self, client, app):
        """Test that deleted expense is removed from database."""
        # Create expense
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        # Verify expense exists in database
        with app.app_context():
            from app.models.expense import Expense
            existing_expense = db.session.get(Expense, expense_id)
            assert existing_expense is not None
        
        # Delete expense
        response = client.delete(f'/api/expenses/{expense_id}')
        assert response.status_code == 204
        
        # Verify expense is removed from database
        with app.app_context():
            deleted_expense = db.session.get(Expense, expense_id)
            assert deleted_expense is None
    
    def test_delete_expense_multiple_times(self, client):
        """Test deleting the same expense multiple times."""
        # Create expense
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        # First deletion should succeed
        response = client.delete(f'/api/expenses/{expense_id}')
        assert response.status_code == 204
        
        # Second deletion should return 404
        response = client.delete(f'/api/expenses/{expense_id}')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == 'NOT_FOUND'
    
    def test_delete_expense_does_not_affect_others(self, client):
        """Test that deleting one expense doesn't affect others."""
        # Create multiple expenses
        expense1 = self.create_sample_expense(client)
        expense2_data = {
            'amount': '15.00',
            'description': 'Bus ticket',
            'category': 'Transport'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(expense2_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        expense2 = json.loads(response.data)
        
        # Delete first expense
        response = client.delete(f'/api/expenses/{expense1["id"]}')
        assert response.status_code == 204
        
        # Verify first expense is deleted
        response = client.get(f'/api/expenses/{expense1["id"]}')
        assert response.status_code == 404
        
        # Verify second expense still exists
        response = client.get(f'/api/expenses/{expense2["id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == expense2['id']
        assert data['description'] == 'Bus ticket'
    
    def test_delete_expense_updates_list(self, client):
        """Test that deleting expense updates the expense list."""
        # Create multiple expenses
        expenses = []
        for i in range(3):
            expense_data = {
                'amount': f'{10 + i}.00',
                'description': f'Test expense {i + 1}',
                'category': 'Test'
            }
            
            response = client.post(
                '/api/expenses',
                data=json.dumps(expense_data),
                content_type='application/json'
            )
            assert response.status_code == 201
            expenses.append(json.loads(response.data))
        
        # Verify all expenses exist
        response = client.get('/api/expenses')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['expenses']) == 3
        assert data['pagination']['total_count'] == 3
        
        # Delete middle expense
        response = client.delete(f'/api/expenses/{expenses[1]["id"]}')
        assert response.status_code == 204
        
        # Verify expense list is updated
        response = client.get('/api/expenses')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['expenses']) == 2
        assert data['pagination']['total_count'] == 2
        
        # Verify correct expenses remain
        remaining_ids = [expense['id'] for expense in data['expenses']]
        assert expenses[0]['id'] in remaining_ids
        assert expenses[2]['id'] in remaining_ids
        assert expenses[1]['id'] not in remaining_ids
    
    def test_delete_expense_with_special_characters(self, client):
        """Test deleting expense with special characters in data."""
        # Create expense with special characters
        expense_data = {
            'amount': '25.50',
            'description': 'Café & Pastry (50% off!)',
            'category': 'Food & Drinks'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(expense_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        expense = json.loads(response.data)
        
        # Delete expense
        response = client.delete(f'/api/expenses/{expense["id"]}')
        assert response.status_code == 204
        
        # Verify deletion
        response = client.get(f'/api/expenses/{expense["id"]}')
        assert response.status_code == 404
    
    def test_delete_expense_concurrent_operations(self, client):
        """Test deletion doesn't interfere with other operations."""
        # Create expense
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        # Create another expense
        expense2_data = {
            'amount': '30.00',
            'description': 'Another expense'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(expense2_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        expense2 = json.loads(response.data)
        
        # Delete first expense
        response = client.delete(f'/api/expenses/{expense_id}')
        assert response.status_code == 204
        
        # Update second expense (should still work)
        update_data = {'amount': '35.00'}
        response = client.put(
            f'/api/expenses/{expense2["id"]}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Create new expense (should still work)
        new_expense_data = {
            'amount': '20.00',
            'description': 'New expense after deletion'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(new_expense_data),
            content_type='application/json'
        )
        assert response.status_code == 201
    
    def test_delete_expense_response_headers(self, client):
        """Test that deletion response has correct headers."""
        # Create expense
        expense = self.create_sample_expense(client)
        expense_id = expense['id']
        
        # Delete expense
        response = client.delete(f'/api/expenses/{expense_id}')
        
        assert response.status_code == 204
        assert response.content_length == 0 or response.content_length is None
        # Response should have no body
        assert len(response.data) == 0