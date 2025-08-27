"""
Performance tests for pagination and summary endpoints.

These tests verify that the API endpoints perform well under load
and with large datasets, ensuring acceptable response times and
resource usage.
"""
import time
import pytest
from datetime import datetime, timedelta
from tests.fixtures import ExpenseFactory


class TestPaginationPerformance:
    """Test performance of pagination endpoints with large datasets."""
    
    @pytest.fixture(scope='function')
    def large_dataset(self, client):
        """Create a large dataset for performance testing."""
        # Create 100 expenses for performance testing
        expenses_data = []
        base_date = datetime(2025, 1, 1)
        categories = ['Food', 'Transport', 'Entertainment', 'Utilities', 'Shopping', 'Health', 'Education']
        
        for i in range(100):
            expense_data = {
                'amount': f'{(i % 50 + 1) * 5}.{i % 100:02d}',
                'description': f'Performance test expense {i+1}',
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
    
    def test_pagination_response_time(self, client, large_dataset):
        """Test that pagination responses are returned within acceptable time limits."""
        # Test different page sizes
        page_sizes = [10, 20, 50]
        max_response_time = 1.0  # 1 second maximum
        
        for page_size in page_sizes:
            start_time = time.time()
            
            response = client.get(f'/api/expenses?page=1&per_page={page_size}')
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < max_response_time, f"Page size {page_size} took {response_time:.2f}s"
            
            # Verify correct number of items returned
            data = response.get_json()
            assert len(data['expenses']) == min(page_size, 100)
    
    def test_deep_pagination_performance(self, client, large_dataset):
        """Test performance of deep pagination (later pages)."""
        max_response_time = 1.0  # 1 second maximum
        
        # Test accessing later pages
        pages_to_test = [1, 5, 10]  # Pages 1, 5, and 10 with 10 items per page
        
        for page in pages_to_test:
            start_time = time.time()
            
            response = client.get(f'/api/expenses?page={page}&per_page=10')
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < max_response_time, f"Page {page} took {response_time:.2f}s"
            
            # Verify pagination metadata
            data = response.get_json()
            assert data['pagination']['page'] == page
            assert data['pagination']['per_page'] == 10
    
    def test_filtered_pagination_performance(self, client, large_dataset):
        """Test performance of pagination with filters applied."""
        max_response_time = 1.0  # 1 second maximum
        
        # Test category filtering with pagination
        start_time = time.time()
        
        response = client.get('/api/expenses?category=Food&page=1&per_page=20')
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < max_response_time, f"Filtered pagination took {response_time:.2f}s"
        
        # Verify all results match filter
        data = response.get_json()
        for expense in data['expenses']:
            assert expense['category'] == 'Food'
    
    def test_sorted_pagination_performance(self, client, large_dataset):
        """Test performance of pagination with sorting applied."""
        max_response_time = 1.0  # 1 second maximum
        
        # Test sorting by different fields
        sort_fields = ['amount', 'date', 'category']
        
        for sort_field in sort_fields:
            start_time = time.time()
            
            response = client.get(f'/api/expenses?sort_by={sort_field}&sort_order=desc&page=1&per_page=20')
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < max_response_time, f"Sorting by {sort_field} took {response_time:.2f}s"
            
            # Verify sorting is applied
            data = response.get_json()
            assert len(data['expenses']) > 0


class TestSummaryPerformance:
    """Test performance of summary endpoints with large datasets."""
    
    @pytest.fixture(scope='function')
    def summary_dataset(self, client):
        """Create a dataset optimized for summary performance testing."""
        # Create 200 expenses across multiple categories and dates
        expenses_data = []
        base_date = datetime(2024, 1, 1)
        categories = ['Food', 'Transport', 'Entertainment', 'Utilities', 'Shopping', 'Health', 'Education', 'Travel']
        
        for i in range(200):
            expense_data = {
                'amount': f'{(i % 100 + 1) * 2}.{i % 100:02d}',
                'description': f'Summary test expense {i+1}',
                'category': categories[i % len(categories)],
                'date': (base_date + timedelta(days=i % 365)).isoformat()
            }
            expenses_data.append(expense_data)
        
        # Batch create expenses
        created_expenses = []
        for expense_data in expenses_data:
            response = client.post('/api/expenses', json=expense_data)
            assert response.status_code == 201
            created_expenses.append(response.get_json())
        
        return created_expenses
    
    def test_overall_summary_performance(self, client, summary_dataset):
        """Test performance of overall summary calculation."""
        max_response_time = 2.0  # 2 seconds maximum for summary calculation
        
        start_time = time.time()
        
        response = client.get('/api/expenses/summary')
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < max_response_time, f"Summary calculation took {response_time:.2f}s"
        
        # Verify summary data structure
        data = response.get_json()
        assert 'total_amount' in data
        assert 'expense_count' in data
        assert 'categories' in data
        assert data['expense_count'] == 200
        assert len(data['categories']) == 8  # All categories should be present
    
    def test_date_range_summary_performance(self, client, summary_dataset):
        """Test performance of date-filtered summary calculation."""
        max_response_time = 2.0  # 2 seconds maximum
        
        # Test different date ranges
        date_ranges = [
            ('2024-01-01T00:00:00Z', '2024-03-31T23:59:59Z'),  # 3 months
            ('2024-01-01T00:00:00Z', '2024-06-30T23:59:59Z'),  # 6 months
            ('2024-01-01T00:00:00Z', '2024-12-31T23:59:59Z'),  # Full year
        ]
        
        for start_date, end_date in date_ranges:
            start_time = time.time()
            
            response = client.get(f'/api/expenses/summary?start_date={start_date}&end_date={end_date}')
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < max_response_time, f"Date range summary took {response_time:.2f}s"
            
            # Verify date range is applied
            data = response.get_json()
            assert data['date_range']['start'] == start_date
            assert data['date_range']['end'] == end_date
    
    def test_category_aggregation_performance(self, client, summary_dataset):
        """Test performance of category aggregation in summaries."""
        max_response_time = 2.0  # 2 seconds maximum
        
        start_time = time.time()
        
        response = client.get('/api/expenses/summary')
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < max_response_time, f"Category aggregation took {response_time:.2f}s"
        
        # Verify category aggregation accuracy
        data = response.get_json()
        categories = data['categories']
        
        # Verify all categories have positive amounts and counts
        for category in categories:
            assert float(category['amount']) > 0
            assert category['count'] > 0
            assert category['category'] in ['Food', 'Transport', 'Entertainment', 'Utilities', 'Shopping', 'Health', 'Education', 'Travel']
        
        # Verify totals match
        total_from_categories = sum(float(cat['amount']) for cat in categories)
        count_from_categories = sum(cat['count'] for cat in categories)
        
        assert abs(total_from_categories - float(data['total_amount'])) < 0.01
        assert count_from_categories == data['expense_count']


class TestConcurrentRequestPerformance:
    """Test performance under concurrent request scenarios."""
    
    def test_concurrent_read_performance(self, client, created_expenses):
        """Test performance of concurrent read operations."""
        import threading
        import queue
        
        max_response_time = 2.0  # 2 seconds maximum per request
        num_concurrent_requests = 5
        
        results_queue = queue.Queue()
        
        def make_request():
            """Make a request and record the response time."""
            start_time = time.time()
            response = client.get('/api/expenses?page=1&per_page=10')
            end_time = time.time()
            
            results_queue.put({
                'status_code': response.status_code,
                'response_time': end_time - start_time
            })
        
        # Create and start threads
        threads = []
        for _ in range(num_concurrent_requests):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests completed successfully and within time limit
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        assert len(results) == num_concurrent_requests
        
        for result in results:
            assert result['status_code'] == 200
            assert result['response_time'] < max_response_time, f"Concurrent request took {result['response_time']:.2f}s"
    
    def test_mixed_operation_performance(self, client):
        """Test performance of mixed read/write operations."""
        max_response_time = 2.0  # 2 seconds maximum per operation
        
        operations = [
            ('GET', '/api/expenses', None),
            ('POST', '/api/expenses', ExpenseFactory.build_expense_data()),
            ('GET', '/api/expenses/summary', None),
            ('GET', '/api/categories', None),
        ]
        
        for method, endpoint, data in operations:
            start_time = time.time()
            
            if method == 'GET':
                response = client.get(endpoint)
            elif method == 'POST':
                response = client.post(endpoint, json=data)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code in [200, 201]
            assert response_time < max_response_time, f"{method} {endpoint} took {response_time:.2f}s"


class TestMemoryUsagePerformance:
    """Test memory usage patterns during operations."""
    
    def test_large_result_set_memory(self, client, large_dataset):
        """Test memory usage when handling large result sets."""
        # Request large page size to test memory handling
        response = client.get('/api/expenses?page=1&per_page=100')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify we can handle large result sets
        assert len(data['expenses']) == 100
        assert 'pagination' in data
        
        # Verify response structure is consistent
        for expense in data['expenses']:
            assert 'id' in expense
            assert 'amount' in expense
            assert 'description' in expense
            assert 'category' in expense
            assert 'date' in expense
    
    def test_summary_calculation_memory(self, client, summary_dataset):
        """Test memory usage during summary calculations."""
        # Request summary which requires aggregation of all data
        response = client.get('/api/expenses/summary')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify summary can handle large datasets
        assert data['expense_count'] == 200
        assert len(data['categories']) > 0
        assert float(data['total_amount']) > 0
        
        # Verify category breakdown is complete
        total_count = sum(cat['count'] for cat in data['categories'])
        assert total_count == data['expense_count']


class TestDatabaseQueryPerformance:
    """Test database query performance and optimization."""
    
    def test_indexed_query_performance(self, client, large_dataset):
        """Test performance of queries that should use database indexes."""
        max_response_time = 1.0  # 1 second maximum
        
        # Test date-based filtering (should use date index)
        start_time = time.time()
        response = client.get('/api/expenses?start_date=2025-01-01T00:00:00Z&end_date=2025-01-15T23:59:59Z')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < max_response_time, "Date filtering query too slow"
        
        # Test category-based filtering (should use category index)
        start_time = time.time()
        response = client.get('/api/expenses?category=Food')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < max_response_time, "Category filtering query too slow"
    
    def test_aggregation_query_performance(self, client, summary_dataset):
        """Test performance of aggregation queries used in summaries."""
        max_response_time = 2.0  # 2 seconds maximum for aggregation
        
        start_time = time.time()
        response = client.get('/api/expenses/summary')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < max_response_time, "Aggregation query too slow"
        
        # Verify aggregation results are accurate
        data = response.get_json()
        assert data['expense_count'] > 0
        assert float(data['total_amount']) > 0
        assert len(data['categories']) > 0


class TestScalabilityIndicators:
    """Test indicators of system scalability."""
    
    def test_response_time_consistency(self, client, large_dataset):
        """Test that response times remain consistent across multiple requests."""
        response_times = []
        num_requests = 10
        
        for _ in range(num_requests):
            start_time = time.time()
            response = client.get('/api/expenses?page=1&per_page=20')
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        # Verify consistency (max time shouldn't be more than 3x average)
        assert max_time < (avg_time * 3), f"Response time inconsistent: avg={avg_time:.3f}s, max={max_time:.3f}s"
        assert avg_time < 1.0, f"Average response time too high: {avg_time:.3f}s"
    
    def test_pagination_efficiency(self, client, large_dataset):
        """Test that pagination remains efficient across different page sizes."""
        page_sizes = [5, 10, 20, 50]
        
        for page_size in page_sizes:
            start_time = time.time()
            response = client.get(f'/api/expenses?page=1&per_page={page_size}')
            end_time = time.time()
            
            assert response.status_code == 200
            
            # Response time should scale reasonably with page size
            # Larger pages should not be dramatically slower
            response_time = end_time - start_time
            assert response_time < 1.0, f"Page size {page_size} took {response_time:.3f}s"
            
            # Verify correct number of items
            data = response.get_json()
            expected_items = min(page_size, 100)  # 100 items in large_dataset
            assert len(data['expenses']) == expected_items