"""
Tests for comprehensive error handling and edge cases.
"""
import json
import pytest
from app import create_app, db


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


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check_success(self, client):
        """Test successful health check."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['status'] == 'healthy'
        assert data['service'] == 'expense-tracker'
        assert data['version'] == '1.0.0'
        assert data['database'] == 'connected'
    
    def test_health_check_methods(self, client):
        """Test health check only accepts GET method."""
        # POST should not be allowed
        response = client.post('/api/health')
        assert response.status_code == 405
        
        data = json.loads(response.data)
        assert data['error']['code'] == 'METHOD_NOT_ALLOWED'
        
        # PUT should not be allowed
        response = client.put('/api/health')
        assert response.status_code == 405
        
        # DELETE should not be allowed
        response = client.delete('/api/health')
        assert response.status_code == 405


class TestGlobalErrorHandlers:
    """Test global error handlers."""
    
    def test_404_not_found(self, client):
        """Test 404 error handling for non-existent endpoints."""
        response = client.get('/api/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        
        assert 'error' in data
        assert data['error']['code'] == 'NOT_FOUND'
        assert data['error']['message'] == 'Resource not found'
    
    def test_405_method_not_allowed(self, client):
        """Test 405 error handling for invalid methods."""
        # Try PATCH on expenses endpoint (not supported)
        response = client.patch('/api/expenses')
        
        assert response.status_code == 405
        data = json.loads(response.data)
        
        assert 'error' in data
        assert data['error']['code'] == 'METHOD_NOT_ALLOWED'
        assert data['error']['message'] == 'Method not allowed for this endpoint'


class TestContentTypeValidation:
    """Test content type validation."""
    
    def test_create_expense_no_content_type(self, client):
        """Test expense creation without content type."""
        expense_data = {
            'amount': '25.50',
            'description': 'Test expense'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(expense_data)
            # No content_type specified
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['error']['code'] == 'INVALID_CONTENT_TYPE'
        assert 'application/json' in data['error']['message']
    
    def test_create_expense_wrong_content_type(self, client):
        """Test expense creation with wrong content type."""
        expense_data = {
            'amount': '25.50',
            'description': 'Test expense'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(expense_data),
            content_type='text/plain'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['error']['code'] == 'INVALID_CONTENT_TYPE'
    
    def test_update_expense_no_content_type(self, client):
        """Test expense update without content type."""
        # First create an expense
        expense_data = {
            'amount': '25.50',
            'description': 'Test expense'
        }
        
        create_response = client.post(
            '/api/expenses',
            data=json.dumps(expense_data),
            content_type='application/json'
        )
        
        assert create_response.status_code == 201
        created_expense = json.loads(create_response.data)
        expense_id = created_expense['id']
        
        # Try to update without content type
        update_data = {'description': 'Updated description'}
        
        response = client.put(
            f'/api/expenses/{expense_id}',
            data=json.dumps(update_data)
            # No content_type specified
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['error']['code'] == 'INVALID_CONTENT_TYPE'


class TestJSONValidation:
    """Test JSON validation."""
    
    def test_create_expense_invalid_json(self, client):
        """Test expense creation with invalid JSON."""
        response = client.post(
            '/api/expenses',
            data='invalid json {',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['error']['code'] == 'INVALID_JSON'
        assert 'Invalid JSON payload' in data['error']['message']
    
    def test_create_expense_null_json(self, client):
        """Test expense creation with null JSON."""
        response = client.post(
            '/api/expenses',
            data='null',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['error']['code'] == 'INVALID_JSON'
    
    def test_create_expense_empty_json(self, client):
        """Test expense creation with empty JSON object."""
        response = client.post(
            '/api/expenses',
            data='{}',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_update_expense_invalid_json(self, client):
        """Test expense update with invalid JSON."""
        # First create an expense
        expense_data = {
            'amount': '25.50',
            'description': 'Test expense'
        }
        
        create_response = client.post(
            '/api/expenses',
            data=json.dumps(expense_data),
            content_type='application/json'
        )
        
        assert create_response.status_code == 201
        created_expense = json.loads(create_response.data)
        expense_id = created_expense['id']
        
        # Try to update with invalid JSON
        response = client.put(
            f'/api/expenses/{expense_id}',
            data='invalid json {',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['error']['code'] == 'INVALID_JSON'
    
    def test_update_expense_empty_json(self, client):
        """Test expense update with empty JSON object."""
        # First create an expense
        expense_data = {
            'amount': '25.50',
            'description': 'Test expense'
        }
        
        create_response = client.post(
            '/api/expenses',
            data=json.dumps(expense_data),
            content_type='application/json'
        )
        
        assert create_response.status_code == 201
        created_expense = json.loads(create_response.data)
        expense_id = created_expense['id']
        
        # Try to update with empty JSON
        response = client.put(
            f'/api/expenses/{expense_id}',
            data='{}',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert 'empty' in data['error']['message'].lower()


class TestParameterValidation:
    """Test parameter validation."""
    
    def test_get_expenses_invalid_page(self, client):
        """Test expense retrieval with invalid page parameters."""
        # Zero page
        response = client.get('/api/expenses?page=0')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert 'greater than 0' in data['error']['message']
        
        # Negative page
        response = client.get('/api/expenses?page=-1')
        assert response.status_code == 400
        
        # Non-numeric page
        response = client.get('/api/expenses?page=invalid')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'INVALID_PARAMETERS'
    
    def test_get_expenses_invalid_per_page(self, client):
        """Test expense retrieval with invalid per_page parameters."""
        # Zero per_page
        response = client.get('/api/expenses?per_page=0')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert 'between 1 and 100' in data['error']['message']
        
        # Too large per_page
        response = client.get('/api/expenses?per_page=101')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Non-numeric per_page
        response = client.get('/api/expenses?per_page=invalid')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'INVALID_PARAMETERS'
    
    def test_get_expenses_invalid_sort_by(self, client):
        """Test expense retrieval with invalid sort_by parameter."""
        response = client.get('/api/expenses?sort_by=invalid_field')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert 'Invalid sort field' in data['error']['message']
        assert 'date, amount, category, created_at, description' in data['error']['message']
    
    def test_get_expenses_invalid_sort_order(self, client):
        """Test expense retrieval with invalid sort_order parameter."""
        response = client.get('/api/expenses?sort_order=invalid')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert 'Invalid sort order' in data['error']['message']
        assert 'asc, desc' in data['error']['message']
    
    def test_get_expenses_invalid_dates(self, client):
        """Test expense retrieval with invalid date parameters."""
        # Invalid start_date format
        response = client.get('/api/expenses?start_date=invalid-date')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'INVALID_PARAMETERS'
        
        # Invalid end_date format
        response = client.get('/api/expenses?end_date=not-a-date')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'INVALID_PARAMETERS'
    
    def test_get_expense_summary_invalid_dates(self, client):
        """Test expense summary with invalid date parameters."""
        # Invalid start_date format
        response = client.get('/api/expenses/summary?start_date=invalid-date')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'INVALID_PARAMETERS'
        
        # Invalid end_date format
        response = client.get('/api/expenses/summary?end_date=not-a-date')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'INVALID_PARAMETERS'


class TestExpenseIDValidation:
    """Test expense ID validation."""
    
    def test_get_expense_invalid_id(self, client):
        """Test getting expense with invalid ID."""
        # Zero ID
        response = client.get('/api/expenses/0')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert 'positive integer' in data['error']['message']
        
        # Non-numeric ID (Flask handles this as 404)
        response = client.get('/api/expenses/invalid')
        assert response.status_code == 404
    
    def test_update_expense_invalid_id(self, client):
        """Test updating expense with invalid ID."""
        update_data = {'description': 'Updated'}
        
        # Zero ID
        response = client.put(
            '/api/expenses/0',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert 'positive integer' in data['error']['message']
    
    def test_delete_expense_invalid_id(self, client):
        """Test deleting expense with invalid ID."""
        # Zero ID
        response = client.delete('/api/expenses/0')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert 'positive integer' in data['error']['message']
    
    def test_expense_not_found(self, client):
        """Test operations on non-existent expense."""
        # Get non-existent expense
        response = client.get('/api/expenses/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error']['code'] == 'NOT_FOUND'
        
        # Update non-existent expense
        update_data = {'description': 'Updated'}
        response = client.put(
            '/api/expenses/999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error']['code'] == 'NOT_FOUND'
        
        # Delete non-existent expense
        response = client.delete('/api/expenses/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error']['code'] == 'NOT_FOUND'


class TestValidationErrors:
    """Test validation error scenarios."""
    
    def test_create_expense_missing_required_fields(self, client):
        """Test expense creation with missing required fields."""
        # Missing amount
        response = client.post(
            '/api/expenses',
            data=json.dumps({'description': 'Test'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Missing description
        response = client.post(
            '/api/expenses',
            data=json.dumps({'amount': '25.50'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_create_expense_invalid_amount(self, client):
        """Test expense creation with invalid amounts."""
        # Negative amount
        response = client.post(
            '/api/expenses',
            data=json.dumps({
                'amount': '-10.00',
                'description': 'Test'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Zero amount
        response = client.post(
            '/api/expenses',
            data=json.dumps({
                'amount': '0.00',
                'description': 'Test'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Non-numeric amount
        response = client.post(
            '/api/expenses',
            data=json.dumps({
                'amount': 'not_a_number',
                'description': 'Test'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_create_expense_invalid_description(self, client):
        """Test expense creation with invalid descriptions."""
        # Empty description
        response = client.post(
            '/api/expenses',
            data=json.dumps({
                'amount': '25.50',
                'description': ''
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Whitespace-only description
        response = client.post(
            '/api/expenses',
            data=json.dumps({
                'amount': '25.50',
                'description': '   '
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Too long description
        response = client.post(
            '/api/expenses',
            data=json.dumps({
                'amount': '25.50',
                'description': 'x' * 256  # Exceeds 255 character limit
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'VALIDATION_ERROR'


class TestErrorResponseFormat:
    """Test that all error responses follow consistent format."""
    
    def test_error_response_structure(self, client):
        """Test that all error responses have consistent structure."""
        # Test various error scenarios
        error_scenarios = [
            ('/api/nonexistent', 'GET', None, None),  # 404
            ('/api/expenses', 'PATCH', None, None),   # 405
            ('/api/expenses', 'POST', 'invalid json', 'application/json'),  # 400
            ('/api/expenses?page=0', 'GET', None, None),  # 400
        ]
        
        for url, method, data, content_type in error_scenarios:
            if method == 'GET':
                response = client.get(url)
            elif method == 'POST':
                response = client.post(url, data=data, content_type=content_type)
            elif method == 'PATCH':
                response = client.patch(url)
            
            # All error responses should have consistent structure
            assert response.status_code >= 400
            response_data = json.loads(response.data)
            
            assert 'error' in response_data
            assert 'code' in response_data['error']
            assert 'message' in response_data['error']
            assert isinstance(response_data['error']['code'], str)
            assert isinstance(response_data['error']['message'], str)
            assert len(response_data['error']['code']) > 0
            assert len(response_data['error']['message']) > 0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_large_pagination_values(self, client):
        """Test pagination with large values."""
        # Very large page number (should not crash)
        response = client.get('/api/expenses?page=999999')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['expenses'] == []  # Should return empty list
        assert data['pagination']['page'] == 999999
    
    def test_unicode_in_description(self, client):
        """Test expense creation with unicode characters."""
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee ☕ and pastry 🥐',
            'category': 'Food & Drinks'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(expense_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['description'] == 'Coffee ☕ and pastry 🥐'
        assert data['category'] == 'Food & Drinks'
    
    def test_special_characters_in_category(self, client):
        """Test expense creation with special characters in category."""
        expense_data = {
            'amount': '25.50',
            'description': 'Test expense',
            'category': 'Food & Drinks / Restaurants'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(expense_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['category'] == 'Food & Drinks / Restaurants'
    
    def test_very_small_amounts(self, client):
        """Test expense creation with very small amounts."""
        expense_data = {
            'amount': '0.01',
            'description': 'Penny expense'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(expense_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['amount'] == '0.01'
    
    def test_very_large_amounts(self, client):
        """Test expense creation with very large amounts."""
        expense_data = {
            'amount': '999999.99',
            'description': 'Large expense'
        }
        
        response = client.post(
            '/api/expenses',
            data=json.dumps(expense_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['amount'] == '999999.99'