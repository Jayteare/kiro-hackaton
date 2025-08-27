"""
End-to-end API tests covering complete user scenarios.

These tests simulate real user workflows and verify that the entire
application stack works correctly from API request to database persistence.
"""
import json
import pytest
from datetime import datetime, timedelta
from tests.fixtures import ExpenseFactory, APITestData


class TestCompleteExpenseLifecycle:
    """Test complete expense lifecycle from creation to deletion."""
    
    def test_expense_crud_lifecycle(self, client):
        """Test complete CRUD lifecycle for a single expense."""
        # 1. Create expense
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee and pastry',
            'category': 'Food',
            'date': '2025-01-15T10:30:00Z'
        }
        
        create_response = client.post(
            '/api/expenses',
            json=expense_data,
            content_type='application/json'
        )
        
        assert create_response.status_code == 201
        created_expense = create_response.get_json()
        expense_id = created_expense['id']
        
        # Verify created expense data
        assert created_expense['amount'] == '25.50'
        assert created_expense['description'] == 'Coffee and pastry'
        assert created_expense['category'] == 'Food'
        assert 'id' in created_expense
        assert 'created_at' in created_expense
        assert 'updated_at' in created_expense
        
        # 2. Read expense
        get_response = client.get(f'/api/expenses/{expense_id}')
        
        assert get_response.status_code == 200
        retrieved_expense = get_response.get_json()
        
        assert retrieved_expense['id'] == expense_id
        assert retrieved_expense['amount'] == '25.50'
        assert retrieved_expense['description'] == 'Coffee and pastry'
        assert retrieved_expense['category'] == 'Food'
        
        # 3. Update expense
        update_data = {
            'amount': '30.00',
            'description': 'Updated coffee and pastry',
            'category': 'Food & Drinks'
        }
        
        update_response = client.put(
            f'/api/expenses/{expense_id}',
            json=update_data,
            content_type='application/json'
        )
        
        assert update_response.status_code == 200
        updated_expense = update_response.get_json()
        
        assert updated_expense['id'] == expense_id
        assert updated_expense['amount'] == '30.00'
        assert updated_expense['description'] == 'Updated coffee and pastry'
        assert updated_expense['category'] == 'Food & Drinks'
        assert updated_expense['updated_at'] != created_expense['updated_at']
        
        # 4. Verify update persisted
        verify_response = client.get(f'/api/expenses/{expense_id}')
        assert verify_response.status_code == 200
        verified_expense = verify_response.get_json()
        assert verified_expense['amount'] == '30.00'
        assert verified_expense['description'] == 'Updated coffee and pastry'
        
        # 5. Delete expense
        delete_response = client.delete(f'/api/expenses/{expense_id}')
        assert delete_response.status_code == 204
        
        # 6. Verify deletion
        get_deleted_response = client.get(f'/api/expenses/{expense_id}')
        assert get_deleted_response.status_code == 404
    
    def test_partial_update_lifecycle(self, client):
        """Test partial update scenarios."""
        # Create expense
        expense_data = ExpenseFactory.build_expense_data()
        create_response = client.post('/api/expenses', json=expense_data)
        assert create_response.status_code == 201
        expense_id = create_response.get_json()['id']
        
        # Update only amount
        update_response = client.put(
            f'/api/expenses/{expense_id}',
            json={'amount': '50.00'}
        )
        assert update_response.status_code == 200
        updated = update_response.get_json()
        assert updated['amount'] == '50.00'
        assert updated['description'] == expense_data['description']  # Unchanged
        
        # Update only description
        update_response = client.put(
            f'/api/expenses/{expense_id}',
            json={'description': 'New description'}
        )
        assert update_response.status_code == 200
        updated = update_response.get_json()
        assert updated['description'] == 'New description'
        assert updated['amount'] == '50.00'  # Previous update preserved
        
        # Update only category
        update_response = client.put(
            f'/api/expenses/{expense_id}',
            json={'category': 'New Category'}
        )
        assert update_response.status_code == 200
        updated = update_response.get_json()
        assert updated['category'] == 'New Category'
        assert updated['description'] == 'New description'  # Previous update preserved


class TestExpenseListingAndFiltering:
    """Test expense listing, pagination, filtering, and sorting scenarios."""
    
    def test_expense_listing_workflow(self, client, created_expenses):
        """Test complete expense listing workflow."""
        # 1. Get all expenses (default pagination)
        response = client.get('/api/expenses')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'expenses' in data
        assert 'pagination' in data
        assert len(data['expenses']) <= 20  # Default page size
        assert data['pagination']['total_count'] == 12
        
        # 2. Test pagination
        page1_response = client.get('/api/expenses?page=1&per_page=5')
        assert page1_response.status_code == 200
        page1_data = page1_response.get_json()
        
        assert len(page1_data['expenses']) == 5
        assert page1_data['pagination']['page'] == 1
        assert page1_data['pagination']['per_page'] == 5
        assert page1_data['pagination']['has_next'] is True
        assert page1_data['pagination']['has_prev'] is False
        
        page2_response = client.get('/api/expenses?page=2&per_page=5')
        assert page2_response.status_code == 200
        page2_data = page2_response.get_json()
        
        assert len(page2_data['expenses']) == 5
        assert page2_data['pagination']['page'] == 2
        assert page2_data['pagination']['has_next'] is True
        assert page2_data['pagination']['has_prev'] is True
        
        # Verify different expenses on different pages
        page1_ids = {exp['id'] for exp in page1_data['expenses']}
        page2_ids = {exp['id'] for exp in page2_data['expenses']}
        assert page1_ids.isdisjoint(page2_ids)
    
    def test_filtering_workflow(self, client, created_expenses):
        """Test expense filtering workflow."""
        # Filter by category
        food_response = client.get('/api/expenses?category=Food')
        assert food_response.status_code == 200
        food_data = food_response.get_json()
        
        # Verify all returned expenses are Food category
        for expense in food_data['expenses']:
            assert expense['category'] == 'Food'
        
        # Filter by date range
        start_date = '2025-01-02T00:00:00Z'
        end_date = '2025-01-05T23:59:59Z'
        
        date_response = client.get(
            f'/api/expenses?start_date={start_date}&end_date={end_date}'
        )
        assert date_response.status_code == 200
        date_data = date_response.get_json()
        
        # Verify all expenses are within date range
        for expense in date_data['expenses']:
            expense_date = datetime.fromisoformat(expense['date'].replace('Z', '+00:00'))
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            assert start_dt <= expense_date <= end_dt
    
    def test_sorting_workflow(self, client, created_expenses):
        """Test expense sorting workflow."""
        # Sort by amount ascending
        asc_response = client.get('/api/expenses?sort_by=amount&sort_order=asc')
        assert asc_response.status_code == 200
        asc_data = asc_response.get_json()
        
        amounts = [float(exp['amount']) for exp in asc_data['expenses']]
        assert amounts == sorted(amounts)
        
        # Sort by amount descending
        desc_response = client.get('/api/expenses?sort_by=amount&sort_order=desc')
        assert desc_response.status_code == 200
        desc_data = desc_response.get_json()
        
        amounts = [float(exp['amount']) for exp in desc_data['expenses']]
        assert amounts == sorted(amounts, reverse=True)
        
        # Sort by date (default order should be newest first)
        date_response = client.get('/api/expenses?sort_by=date&sort_order=desc')
        assert date_response.status_code == 200
        date_data = date_response.get_json()
        
        dates = [exp['date'] for exp in date_data['expenses']]
        assert dates == sorted(dates, reverse=True)
    
    def test_combined_filtering_and_pagination(self, client, created_expenses):
        """Test combining filters with pagination."""
        # Filter by category with pagination
        response = client.get('/api/expenses?category=Food&page=1&per_page=2')
        assert response.status_code == 200
        
        data = response.get_json()
        assert len(data['expenses']) <= 2
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 2
        
        # All expenses should be Food category
        for expense in data['expenses']:
            assert expense['category'] == 'Food'


class TestExpenseSummaryWorkflow:
    """Test expense summary and reporting workflows."""
    
    def test_complete_summary_workflow(self, client, created_expenses):
        """Test complete expense summary workflow."""
        # 1. Get overall summary
        summary_response = client.get('/api/expenses/summary')
        assert summary_response.status_code == 200
        
        summary_data = summary_response.get_json()
        assert 'total_amount' in summary_data
        assert 'expense_count' in summary_data
        assert 'categories' in summary_data
        assert 'date_range' in summary_data
        
        assert summary_data['expense_count'] == 12
        assert float(summary_data['total_amount']) > 0
        assert len(summary_data['categories']) > 0
        
        # 2. Get summary with date range
        start_date = '2025-01-01T00:00:00Z'
        end_date = '2025-01-05T23:59:59Z'
        
        date_summary_response = client.get(
            f'/api/expenses/summary?start_date={start_date}&end_date={end_date}'
        )
        assert date_summary_response.status_code == 200
        
        date_summary = date_summary_response.get_json()
        assert date_summary['expense_count'] <= summary_data['expense_count']
        assert date_summary['date_range']['start'] == start_date
        assert date_summary['date_range']['end'] == end_date
        
        # 3. Verify category breakdown
        total_from_categories = sum(
            float(cat['amount']) for cat in summary_data['categories']
        )
        assert abs(total_from_categories - float(summary_data['total_amount'])) < 0.01
        
        # 4. Verify category counts
        total_count_from_categories = sum(
            cat['count'] for cat in summary_data['categories']
        )
        assert total_count_from_categories == summary_data['expense_count']


class TestCategoryManagement:
    """Test category management workflows."""
    
    def test_category_listing_workflow(self, client, created_expenses):
        """Test category listing workflow."""
        # Get all categories
        categories_response = client.get('/api/categories')
        assert categories_response.status_code == 200
        
        categories_data = categories_response.get_json()
        assert 'categories' in categories_data
        assert isinstance(categories_data['categories'], list)
        assert len(categories_data['categories']) > 0
        
        # Verify categories are sorted
        categories = categories_data['categories']
        assert categories == sorted(categories)
        
        # Verify expected categories exist
        expected_categories = {'Food', 'Transport', 'Entertainment', 'Utilities', 'Shopping'}
        actual_categories = set(categories)
        assert expected_categories.issubset(actual_categories)
    
    def test_category_filtering_integration(self, client, created_expenses):
        """Test integration between category listing and filtering."""
        # Get all categories
        categories_response = client.get('/api/categories')
        categories = categories_response.get_json()['categories']
        
        # Test filtering by each category
        for category in categories:
            filter_response = client.get(f'/api/expenses?category={category}')
            assert filter_response.status_code == 200
            
            filtered_data = filter_response.get_json()
            # All returned expenses should match the category
            for expense in filtered_data['expenses']:
                assert expense['category'] == category


class TestErrorHandlingWorkflows:
    """Test error handling in complete workflows."""
    
    def test_invalid_expense_workflow(self, client):
        """Test workflow with invalid expense data."""
        # Try to create invalid expense
        invalid_data = {
            'amount': '-10.00',  # Invalid negative amount
            'description': '',   # Invalid empty description
        }
        
        create_response = client.post('/api/expenses', json=invalid_data)
        assert create_response.status_code == 400
        
        error_data = create_response.get_json()
        assert 'error' in error_data
        assert error_data['error']['code'] == 'VALIDATION_ERROR'
        
        # Verify no expense was created
        list_response = client.get('/api/expenses')
        assert list_response.status_code == 200
        assert list_response.get_json()['pagination']['total_count'] == 0
    
    def test_nonexistent_expense_workflow(self, client):
        """Test workflow with non-existent expense operations."""
        nonexistent_id = 999
        
        # Try to get non-existent expense
        get_response = client.get(f'/api/expenses/{nonexistent_id}')
        assert get_response.status_code == 404
        
        # Try to update non-existent expense
        update_response = client.put(
            f'/api/expenses/{nonexistent_id}',
            json={'amount': '50.00'}
        )
        assert update_response.status_code == 404
        
        # Try to delete non-existent expense
        delete_response = client.delete(f'/api/expenses/{nonexistent_id}')
        assert delete_response.status_code == 404
        
        # All should return consistent error format
        for response in [get_response, update_response, delete_response]:
            error_data = response.get_json()
            assert 'error' in error_data
            assert error_data['error']['code'] == 'NOT_FOUND'


class TestDataConsistencyWorkflows:
    """Test data consistency across operations."""
    
    def test_expense_count_consistency(self, client):
        """Test that expense counts remain consistent across operations."""
        # Create multiple expenses
        expenses_to_create = 5
        created_ids = []
        
        for i in range(expenses_to_create):
            expense_data = ExpenseFactory.build_expense_data(
                description=f'Test expense {i+1}',
                amount=f'{(i+1)*10}.00'
            )
            
            response = client.post('/api/expenses', json=expense_data)
            assert response.status_code == 201
            created_ids.append(response.get_json()['id'])
        
        # Verify count in list endpoint
        list_response = client.get('/api/expenses')
        assert list_response.status_code == 200
        assert list_response.get_json()['pagination']['total_count'] == expenses_to_create
        
        # Verify count in summary endpoint
        summary_response = client.get('/api/expenses/summary')
        assert summary_response.status_code == 200
        assert summary_response.get_json()['expense_count'] == expenses_to_create
        
        # Delete one expense
        delete_response = client.delete(f'/api/expenses/{created_ids[0]}')
        assert delete_response.status_code == 204
        
        # Verify counts are updated
        list_response = client.get('/api/expenses')
        assert list_response.get_json()['pagination']['total_count'] == expenses_to_create - 1
        
        summary_response = client.get('/api/expenses/summary')
        assert summary_response.get_json()['expense_count'] == expenses_to_create - 1
    
    def test_amount_calculation_consistency(self, client):
        """Test that amount calculations are consistent across endpoints."""
        # Create expenses with known amounts
        amounts = ['10.00', '20.00', '30.00']
        expected_total = 60.00
        
        for amount in amounts:
            expense_data = ExpenseFactory.build_expense_data(amount=amount)
            response = client.post('/api/expenses', json=expense_data)
            assert response.status_code == 201
        
        # Get summary and verify total
        summary_response = client.get('/api/expenses/summary')
        assert summary_response.status_code == 200
        
        summary_data = summary_response.get_json()
        actual_total = float(summary_data['total_amount'])
        assert abs(actual_total - expected_total) < 0.01
        
        # Verify individual expenses sum to total
        list_response = client.get('/api/expenses')
        expenses = list_response.get_json()['expenses']
        
        calculated_total = sum(float(exp['amount']) for exp in expenses)
        assert abs(calculated_total - expected_total) < 0.01


class TestConcurrentOperations:
    """Test scenarios that might occur with concurrent operations."""
    
    def test_create_and_list_consistency(self, client):
        """Test consistency between create and list operations."""
        initial_response = client.get('/api/expenses')
        initial_count = initial_response.get_json()['pagination']['total_count']
        
        # Create expense
        expense_data = ExpenseFactory.build_expense_data()
        create_response = client.post('/api/expenses', json=expense_data)
        assert create_response.status_code == 201
        
        # Immediately list expenses
        list_response = client.get('/api/expenses')
        new_count = list_response.get_json()['pagination']['total_count']
        
        assert new_count == initial_count + 1
        
        # Verify the created expense appears in the list
        expenses = list_response.get_json()['expenses']
        created_id = create_response.get_json()['id']
        
        found_expense = next((exp for exp in expenses if exp['id'] == created_id), None)
        assert found_expense is not None
        assert found_expense['description'] == expense_data['description']
    
    def test_update_and_retrieve_consistency(self, client):
        """Test consistency between update and retrieve operations."""
        # Create expense
        expense_data = ExpenseFactory.build_expense_data()
        create_response = client.post('/api/expenses', json=expense_data)
        expense_id = create_response.get_json()['id']
        
        # Update expense
        update_data = {'description': 'Updated description'}
        update_response = client.put(f'/api/expenses/{expense_id}', json=update_data)
        assert update_response.status_code == 200
        
        # Immediately retrieve expense
        get_response = client.get(f'/api/expenses/{expense_id}')
        assert get_response.status_code == 200
        
        retrieved_expense = get_response.get_json()
        assert retrieved_expense['description'] == 'Updated description'
        
        # Verify update appears in list as well
        list_response = client.get('/api/expenses')
        expenses = list_response.get_json()['expenses']
        
        found_expense = next((exp for exp in expenses if exp['id'] == expense_id), None)
        assert found_expense is not None
        assert found_expense['description'] == 'Updated description'
