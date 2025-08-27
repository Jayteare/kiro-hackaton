"""
Tests for Marshmallow schemas.
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from marshmallow import ValidationError

from app.schemas.expense_schema import ExpenseSchema, ExpenseCreateSchema, ExpenseUpdateSchema
from app.schemas.summary_schema import SummarySchema, CategorySummarySchema, SummaryRequestSchema


class TestExpenseSchema:
    """Test cases for ExpenseSchema."""
    
    def test_valid_expense_serialization(self):
        """Test serializing a valid expense."""
        schema = ExpenseSchema()
        expense_data = {
            'id': 1,
            'amount': Decimal('25.50'),
            'description': 'Coffee and pastry',
            'category': 'Food',
            'date': datetime(2025, 1, 15, 10, 30, 0),
            'created_at': datetime(2025, 1, 15, 10, 30, 0),
            'updated_at': datetime(2025, 1, 15, 10, 30, 0)
        }
        
        result = schema.dump(expense_data)
        
        assert result['id'] == 1
        assert result['amount'] == '25.50'
        assert result['description'] == 'Coffee and pastry'
        assert result['category'] == 'Food'
        assert 'date' in result
        assert 'created_at' in result
        assert 'updated_at' in result

    def test_valid_expense_deserialization(self):
        """Test deserializing valid expense data."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee and pastry',
            'category': 'Food',
            'date': '2025-01-15T10:30:00'
        }
        
        result = schema.load(expense_data)
        
        assert result['amount'] == Decimal('25.50')
        assert result['description'] == 'Coffee and pastry'
        assert result['category'] == 'Food'
        assert isinstance(result['date'], datetime)

    def test_expense_with_default_category(self):
        """Test expense creation with default category."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee and pastry'
        }
        
        result = schema.load(expense_data)
        
        assert result['category'] == 'Uncategorized'

    def test_expense_with_empty_category(self):
        """Test expense creation with empty category defaults to Uncategorized."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee and pastry',
            'category': ''
        }
        
        result = schema.load(expense_data)
        
        assert result['category'] == 'Uncategorized'

    def test_expense_with_whitespace_category(self):
        """Test expense creation with whitespace-only category."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee and pastry',
            'category': '   '
        }
        
        result = schema.load(expense_data)
        
        assert result['category'] == 'Uncategorized'

    def test_invalid_amount_negative(self):
        """Test validation error for negative amount."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '-25.50',
            'description': 'Coffee and pastry'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(expense_data)
        
        assert 'amount' in exc_info.value.messages

    def test_invalid_amount_zero(self):
        """Test validation error for zero amount."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '0.00',
            'description': 'Coffee and pastry'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(expense_data)
        
        assert 'amount' in exc_info.value.messages

    def test_invalid_amount_non_numeric(self):
        """Test validation error for non-numeric amount."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': 'not_a_number',
            'description': 'Coffee and pastry'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(expense_data)
        
        assert 'amount' in exc_info.value.messages

    def test_missing_required_amount(self):
        """Test validation error for missing amount."""
        schema = ExpenseSchema()
        expense_data = {
            'description': 'Coffee and pastry'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(expense_data)
        
        assert 'amount' in exc_info.value.messages

    def test_missing_required_description(self):
        """Test validation error for missing description."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '25.50'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(expense_data)
        
        assert 'description' in exc_info.value.messages

    def test_empty_description(self):
        """Test validation error for empty description."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '25.50',
            'description': ''
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(expense_data)
        
        assert 'description' in exc_info.value.messages

    def test_whitespace_only_description(self):
        """Test validation error for whitespace-only description."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '25.50',
            'description': '   '
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(expense_data)
        
        assert 'description' in exc_info.value.messages

    def test_description_too_long(self):
        """Test validation error for description exceeding max length."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '25.50',
            'description': 'x' * 256  # Exceeds 255 character limit
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(expense_data)
        
        assert 'description' in exc_info.value.messages

    def test_category_too_long(self):
        """Test validation error for category exceeding max length."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee and pastry',
            'category': 'x' * 101  # Exceeds 100 character limit
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(expense_data)
        
        assert 'category' in exc_info.value.messages

    def test_description_trimming(self):
        """Test that description is trimmed of whitespace."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '25.50',
            'description': '  Coffee and pastry  '
        }
        
        result = schema.load(expense_data)
        
        assert result['description'] == 'Coffee and pastry'

    def test_category_trimming(self):
        """Test that category is trimmed of whitespace."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee and pastry',
            'category': '  Food  '
        }
        
        result = schema.load(expense_data)
        
        assert result['category'] == 'Food'


class TestExpenseCreateSchema:
    """Test cases for ExpenseCreateSchema."""
    
    def test_excludes_readonly_fields(self):
        """Test that create schema excludes read-only fields."""
        schema = ExpenseCreateSchema()
        expense_data = {
            'id': 1,  # Should be ignored
            'amount': '25.50',
            'description': 'Coffee and pastry',
            'created_at': '2025-01-15T10:30:00',  # Should be ignored
            'updated_at': '2025-01-15T10:30:00'   # Should be ignored
        }
        
        result = schema.load(expense_data)
        
        assert 'id' not in result
        assert 'created_at' not in result
        assert 'updated_at' not in result
        assert result['amount'] == Decimal('25.50')
        assert result['description'] == 'Coffee and pastry'


class TestExpenseUpdateSchema:
    """Test cases for ExpenseUpdateSchema."""
    
    def test_partial_update_amount_only(self):
        """Test partial update with only amount."""
        schema = ExpenseUpdateSchema()
        update_data = {
            'amount': '30.00'
        }
        
        result = schema.load(update_data)
        
        assert result['amount'] == Decimal('30.00')
        assert 'description' not in result
        assert 'category' not in result

    def test_partial_update_description_only(self):
        """Test partial update with only description."""
        schema = ExpenseUpdateSchema()
        update_data = {
            'description': 'Updated description'
        }
        
        result = schema.load(update_data)
        
        assert result['description'] == 'Updated description'
        assert 'amount' not in result
        assert 'category' not in result

    def test_empty_update_data(self):
        """Test validation error for empty update data."""
        schema = ExpenseUpdateSchema()
        update_data = {}
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(update_data)
        
        assert 'At least one field must be provided for update' in str(exc_info.value)

    def test_update_with_invalid_amount(self):
        """Test validation error for invalid amount in update."""
        schema = ExpenseUpdateSchema()
        update_data = {
            'amount': '-10.00'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(update_data)
        
        assert 'amount' in exc_info.value.messages

    def test_update_with_empty_description(self):
        """Test validation error for empty description in update."""
        schema = ExpenseUpdateSchema()
        update_data = {
            'description': ''
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(update_data)
        
        assert 'description' in exc_info.value.messages


class TestCategorySummarySchema:
    """Test cases for CategorySummarySchema."""
    
    def test_valid_category_summary(self):
        """Test valid category summary serialization."""
        schema = CategorySummarySchema()
        summary_data = {
            'category': 'Food',
            'amount': Decimal('85.25'),
            'count': 8
        }
        
        result = schema.dump(summary_data)
        
        assert result['category'] == 'Food'
        assert result['amount'] == '85.25'
        assert result['count'] == 8

    def test_invalid_negative_count(self):
        """Test validation error for negative count."""
        schema = CategorySummarySchema()
        summary_data = {
            'category': 'Food',
            'amount': Decimal('85.25'),
            'count': -1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(summary_data)
        
        assert 'count' in exc_info.value.messages


class TestSummarySchema:
    """Test cases for SummarySchema."""
    
    def test_valid_summary(self):
        """Test valid summary serialization."""
        schema = SummarySchema()
        summary_data = {
            'total_amount': Decimal('150.75'),
            'expense_count': 12,
            'date_range': {
                'start': datetime(2025, 1, 1),
                'end': datetime(2025, 1, 31)
            },
            'categories': [
                {
                    'category': 'Food',
                    'amount': Decimal('85.25'),
                    'count': 8
                },
                {
                    'category': 'Transport',
                    'amount': Decimal('65.50'),
                    'count': 4
                }
            ]
        }
        
        result = schema.dump(summary_data)
        
        assert result['total_amount'] == '150.75'
        assert result['expense_count'] == 12
        assert 'date_range' in result
        assert len(result['categories']) == 2

    def test_summary_with_empty_categories(self):
        """Test summary with empty categories list."""
        schema = SummarySchema()
        summary_data = {
            'total_amount': Decimal('0.00'),
            'expense_count': 0,
            'date_range': {
                'start': None,
                'end': None
            },
            'categories': []
        }
        
        result = schema.dump(summary_data)
        
        assert result['total_amount'] == '0.00'
        assert result['expense_count'] == 0
        assert result['categories'] == []

    def test_invalid_negative_total_amount(self):
        """Test validation error for negative total amount."""
        schema = SummarySchema()
        summary_data = {
            'total_amount': Decimal('-10.00'),
            'expense_count': 1,
            'date_range': {'start': None, 'end': None},
            'categories': []
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(summary_data)
        
        assert 'total_amount' in exc_info.value.messages

    def test_invalid_negative_expense_count(self):
        """Test validation error for negative expense count."""
        schema = SummarySchema()
        summary_data = {
            'total_amount': Decimal('10.00'),
            'expense_count': -1,
            'date_range': {'start': None, 'end': None},
            'categories': []
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(summary_data)
        
        assert 'expense_count' in exc_info.value.messages

    def test_duplicate_categories_validation(self):
        """Test validation error for duplicate categories in summary."""
        schema = SummarySchema()
        summary_data = {
            'total_amount': Decimal('100.00'),
            'expense_count': 4,
            'date_range': {'start': None, 'end': None},
            'categories': [
                {'category': 'Food', 'amount': Decimal('50.00'), 'count': 2},
                {'category': 'Food', 'amount': Decimal('50.00'), 'count': 2}  # Duplicate
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(summary_data)
        
        assert 'Duplicate categories found in summary' in str(exc_info.value)


class TestSummaryRequestSchema:
    """Test cases for SummaryRequestSchema."""
    
    def test_valid_date_range_request(self):
        """Test valid summary request with date range."""
        schema = SummaryRequestSchema()
        request_data = {
            'start_date': '2025-01-01T00:00:00',
            'end_date': '2025-01-31T23:59:59'
        }
        
        result = schema.load(request_data)
        
        assert isinstance(result['start_date'], datetime)
        assert isinstance(result['end_date'], datetime)

    def test_request_with_category_filter(self):
        """Test summary request with category filter."""
        schema = SummaryRequestSchema()
        request_data = {
            'category': 'Food'
        }
        
        result = schema.load(request_data)
        
        assert result['category'] == 'Food'

    def test_empty_request(self):
        """Test empty summary request (should be valid)."""
        schema = SummaryRequestSchema()
        request_data = {}
        
        result = schema.load(request_data)
        
        assert result == {}

    def test_invalid_date_format(self):
        """Test validation error for invalid date format."""
        schema = SummaryRequestSchema()
        request_data = {
            'start_date': 'invalid-date'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(request_data)
        
        assert 'start_date' in exc_info.value.messages

    def test_invalid_date_range_start_after_end(self):
        """Test validation error when start_date is after end_date."""
        schema = SummaryRequestSchema()
        request_data = {
            'start_date': '2025-01-31T23:59:59',
            'end_date': '2025-01-01T00:00:00'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(request_data)
        
        assert 'Start date must be before end date' in str(exc_info.value)


class TestSchemaEdgeCases:
    """Test edge cases and error handling for schemas."""
    
    def test_expense_schema_with_very_large_amount(self):
        """Test expense schema with very large amount."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '999999999.99',
            'description': 'Very expensive item'
        }
        
        result = schema.load(expense_data)
        
        assert result['amount'] == Decimal('999999999.99')

    def test_expense_schema_with_very_small_amount(self):
        """Test expense schema with smallest valid amount."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '0.02',  # Use 0.02 since 0.01 is the minimum exclusive
            'description': 'Very cheap item'
        }
        
        result = schema.load(expense_data)
        
        assert result['amount'] == Decimal('0.02')

    def test_expense_schema_with_unicode_description(self):
        """Test expense schema with unicode characters in description."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '25.50',
            'description': 'Café au lait ☕ with émojis 🥐'
        }
        
        result = schema.load(expense_data)
        
        assert result['description'] == 'Café au lait ☕ with émojis 🥐'

    def test_expense_schema_with_unicode_category(self):
        """Test expense schema with unicode characters in category."""
        schema = ExpenseSchema()
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee',
            'category': 'Café & Restaurants'
        }
        
        result = schema.load(expense_data)
        
        assert result['category'] == 'Café & Restaurants'

    def test_expense_update_schema_with_null_values(self):
        """Test update schema behavior with missing fields (not null)."""
        schema = ExpenseUpdateSchema()
        update_data = {
            'amount': '30.00'
            # category is missing, which is fine for partial updates
        }
        
        # This should be valid for updates - missing fields mean don't change
        result = schema.load(update_data)
        
        assert 'amount' in result
        assert result['amount'] == Decimal('30.00')
        assert 'category' not in result  # Missing fields are not included

    def test_summary_schema_with_zero_values(self):
        """Test summary schema with all zero values."""
        schema = SummarySchema()
        summary_data = {
            'total_amount': Decimal('0.00'),
            'expense_count': 0,
            'date_range': {
                'start': None,
                'end': None
            },
            'categories': []
        }
        
        result = schema.dump(summary_data)
        
        assert result['total_amount'] == '0.00'
        assert result['expense_count'] == 0
        assert result['categories'] == []

    def test_category_summary_with_zero_count(self):
        """Test category summary with zero count."""
        schema = CategorySummarySchema()
        summary_data = {
            'category': 'Empty Category',
            'amount': Decimal('0.00'),
            'count': 0
        }
        
        result = schema.dump(summary_data)
        
        assert result['category'] == 'Empty Category'
        assert result['amount'] == '0.00'
        assert result['count'] == 0

    def test_expense_schema_serialization_with_none_values(self):
        """Test expense schema serialization handles None values gracefully."""
        schema = ExpenseSchema()
        expense_data = {
            'id': 1,
            'amount': Decimal('25.50'),
            'description': 'Coffee',
            'category': 'Food',
            'date': datetime(2025, 1, 15, 10, 30, 0),
            'created_at': None,  # This might happen in some edge cases
            'updated_at': None
        }
        
        result = schema.dump(expense_data)
        
        # Should handle None values gracefully
        assert result['id'] == 1
        assert result['amount'] == '25.50'
        assert result['created_at'] is None
        assert result['updated_at'] is None

    def test_expense_create_schema_ignores_extra_fields(self):
        """Test that create schema ignores extra unknown fields."""
        schema = ExpenseCreateSchema()
        expense_data = {
            'amount': '25.50',
            'description': 'Coffee',
            'extra_field': 'should be ignored',
            'another_unknown': 123
        }
        
        result = schema.load(expense_data)
        
        assert 'extra_field' not in result
        assert 'another_unknown' not in result
        assert result['amount'] == Decimal('25.50')
        assert result['description'] == 'Coffee'

    def test_summary_request_schema_with_same_dates(self):
        """Test summary request with same start and end dates."""
        schema = SummaryRequestSchema()
        request_data = {
            'start_date': '2025-01-15T00:00:00',
            'end_date': '2025-01-15T23:59:59'
        }
        
        result = schema.load(request_data)
        
        assert isinstance(result['start_date'], datetime)
        assert isinstance(result['end_date'], datetime)
        # Should be valid even if same day

    def test_expense_schema_with_malformed_json_data(self):
        """Test expense schema with various malformed data types."""
        schema = ExpenseSchema()
        
        # Test with non-string description
        with pytest.raises(ValidationError):
            schema.load({'amount': '25.50', 'description': 123})
        
        # Test with boolean amount
        with pytest.raises(ValidationError):
            schema.load({'amount': True, 'description': 'Test'})

    def test_summary_schema_error_message_format(self):
        """Test that error messages are properly formatted for API responses."""
        schema = SummarySchema()
        
        try:
            schema.load({
                'total_amount': 'invalid',
                'expense_count': 'invalid',
                'categories': 'not_a_list'
            })
        except ValidationError as e:
            # Verify error structure is suitable for API responses
            assert isinstance(e.messages, dict)
            assert 'total_amount' in e.messages
            assert 'expense_count' in e.messages
            assert 'categories' in e.messages