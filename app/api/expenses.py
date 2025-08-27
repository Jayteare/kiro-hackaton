"""
Expense API endpoints for CRUD operations.
"""
from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError as MarshmallowValidationError
from app import db
from app.services.expense_service import (
    ExpenseService, 
    ValidationError, 
    NotFoundError, 
    ExpenseServiceError
)
from app.schemas.expense_schema import ExpenseSchema, ExpenseSummarySchema

# Create blueprint
expenses_bp = Blueprint('expenses', __name__)

# Initialize schema
expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)
summary_schema = ExpenseSummarySchema()


def get_expense_service():
    """Get expense service instance with current database session."""
    return ExpenseService(db.session)


def handle_service_errors(func):
    """Decorator to handle common service errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': str(e)
                }
            }), 400
        except NotFoundError as e:
            return jsonify({
                'error': {
                    'code': 'NOT_FOUND',
                    'message': str(e)
                }
            }), 404
        except ExpenseServiceError as e:
            return jsonify({
                'error': {
                    'code': 'SERVICE_ERROR',
                    'message': str(e)
                }
            }), 500
        except Exception as e:
            current_app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'An unexpected error occurred'
                }
            }), 500
    
    wrapper.__name__ = func.__name__
    return wrapper


@expenses_bp.route('/expenses', methods=['POST'])
@handle_service_errors
def create_expense():
    """
    Create a new expense.
    
    Expected JSON payload:
    {
        "amount": 25.50,
        "description": "Coffee and pastry",
        "category": "Food",  # optional, defaults to "Uncategorized"
        "date": "2025-01-15T10:30:00Z"  # optional, defaults to current time
    }
    
    Returns:
        201: Created expense object
        400: Validation error
        422: Invalid JSON or missing required fields
        500: Server error
    """
    # Validate JSON content type
    if not request.is_json:
        return jsonify({
            'error': {
                'code': 'INVALID_CONTENT_TYPE',
                'message': 'Content-Type must be application/json'
            }
        }), 400
    
    # Get JSON data
    try:
        expense_data = request.get_json()
        if expense_data is None:
            return jsonify({
                'error': {
                    'code': 'INVALID_JSON',
                    'message': 'Invalid JSON payload'
                }
            }), 400
    except Exception:
        return jsonify({
            'error': {
                'code': 'INVALID_JSON',
                'message': 'Invalid JSON payload'
            }
        }), 400
    
    # Create expense through service
    service = get_expense_service()
    expense = service.create_expense(expense_data)
    
    # Serialize response
    result = expense_schema.dump(expense)
    
    return jsonify(result), 201


@expenses_bp.route('/expenses', methods=['GET'])
@handle_service_errors
def get_expenses():
    """
    Get expenses with optional filtering and pagination.
    
    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20, max: 100)
    - category: Filter by category
    - start_date: Filter by start date (ISO format)
    - end_date: Filter by end date (ISO format)
    - sort_by: Sort field (date, amount, category, created_at)
    - sort_order: Sort order (asc, desc)
    
    Returns:
        200: List of expenses with pagination metadata
        400: Invalid query parameters
        500: Server error
    """
    # Parse query parameters
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        category = request.args.get('category')
        sort_by = request.args.get('sort_by', 'date')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Validate pagination parameters
        if page < 1:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Page number must be greater than 0'
                }
            }), 400
        
        if per_page < 1 or per_page > 100:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Per page must be between 1 and 100'
                }
            }), 400
        
        # Validate sort parameters
        valid_sort_fields = ['date', 'amount', 'category', 'created_at', 'description']
        if sort_by not in valid_sort_fields:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': f'Invalid sort field. Must be one of: {", ".join(valid_sort_fields)}'
                }
            }), 400
        
        valid_sort_orders = ['asc', 'desc']
        if sort_order not in valid_sort_orders:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': f'Invalid sort order. Must be one of: {", ".join(valid_sort_orders)}'
                }
            }), 400
        
        # Parse date parameters
        start_date = None
        end_date = None
        
        if request.args.get('start_date'):
            from datetime import datetime
            start_date = datetime.fromisoformat(request.args.get('start_date').replace('Z', '+00:00'))
        
        if request.args.get('end_date'):
            from datetime import datetime
            end_date = datetime.fromisoformat(request.args.get('end_date').replace('Z', '+00:00'))
            
    except (ValueError, TypeError) as e:
        return jsonify({
            'error': {
                'code': 'INVALID_PARAMETERS',
                'message': f'Invalid query parameters: {str(e)}'
            }
        }), 400
    
    # Get expenses through service
    service = get_expense_service()
    expenses, total_count = service.get_expenses(
        page=page,
        per_page=per_page,
        category=category,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Serialize response
    expenses_data = expenses_schema.dump(expenses)
    
    # Calculate pagination metadata
    total_pages = (total_count + per_page - 1) // per_page
    has_next = page < total_pages
    has_prev = page > 1
    
    return jsonify({
        'expenses': expenses_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_count': total_count,
            'total_pages': total_pages,
            'has_next': has_next,
            'has_prev': has_prev
        }
    }), 200


@expenses_bp.route('/expenses/<int:expense_id>', methods=['GET'])
@handle_service_errors
def get_expense(expense_id):
    """
    Get a specific expense by ID.
    
    Args:
        expense_id: Expense ID from URL path
    
    Returns:
        200: Expense object
        400: Invalid expense ID
        404: Expense not found
        500: Server error
    """
    # Validate expense ID
    if expense_id <= 0:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Expense ID must be a positive integer'
            }
        }), 400
    
    # Get expense through service
    service = get_expense_service()
    expense = service.get_expense(expense_id)
    
    # Serialize response
    result = expense_schema.dump(expense)
    
    return jsonify(result), 200


@expenses_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
@handle_service_errors
def update_expense(expense_id):
    """
    Update an existing expense.
    
    Args:
        expense_id: Expense ID from URL path
    
    Expected JSON payload (all fields optional):
    {
        "amount": 30.00,
        "description": "Updated description",
        "category": "Updated category",
        "date": "2025-01-15T10:30:00Z"
    }
    
    Returns:
        200: Updated expense object
        400: Validation error
        404: Expense not found
        422: Invalid JSON
        500: Server error
    """
    # Validate expense ID
    if expense_id <= 0:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Expense ID must be a positive integer'
            }
        }), 400
    
    # Validate JSON content type
    if not request.is_json:
        return jsonify({
            'error': {
                'code': 'INVALID_CONTENT_TYPE',
                'message': 'Content-Type must be application/json'
            }
        }), 400
    
    # Get JSON data
    try:
        update_data = request.get_json()
        if update_data is None:
            return jsonify({
                'error': {
                    'code': 'INVALID_JSON',
                    'message': 'Invalid JSON payload'
                }
            }), 400
    except Exception:
        return jsonify({
            'error': {
                'code': 'INVALID_JSON',
                'message': 'Invalid JSON payload'
            }
        }), 400
    
    # Validate that update data is not empty
    if not update_data:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Update data cannot be empty'
            }
        }), 400
    
    # Update expense through service
    service = get_expense_service()
    expense = service.update_expense(expense_id, update_data)
    
    # Serialize response
    result = expense_schema.dump(expense)
    
    return jsonify(result), 200


@expenses_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@handle_service_errors
def delete_expense(expense_id):
    """
    Delete an expense by ID.
    
    Args:
        expense_id: Expense ID from URL path
    
    Returns:
        204: Expense deleted successfully
        400: Invalid expense ID
        404: Expense not found
        500: Server error
    """
    # Validate expense ID
    if expense_id <= 0:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Expense ID must be a positive integer'
            }
        }), 400
    
    # Delete expense through service
    service = get_expense_service()
    service.delete_expense(expense_id)
    
    return '', 204


@expenses_bp.route('/categories', methods=['GET'])
@handle_service_errors
def get_categories():
    """
    Get all available expense categories.
    
    Returns:
        200: List of unique category names
        500: Server error
    """
    # Get categories through service
    service = get_expense_service()
    categories = service.get_categories()
    
    return jsonify({
        'categories': categories
    }), 200


@expenses_bp.route('/expenses/summary', methods=['GET'])
@handle_service_errors
def get_expense_summary():
    """
    Get expense summary with category breakdown and optional date filtering.
    
    Query parameters:
    - start_date: Filter by start date (ISO format, optional)
    - end_date: Filter by end date (ISO format, optional)
    
    Returns:
        200: Expense summary with total amount, count, and category breakdown
        400: Invalid query parameters
        500: Server error
    """
    # Parse query parameters
    try:
        start_date = None
        end_date = None
        
        if request.args.get('start_date'):
            from datetime import datetime
            start_date = datetime.fromisoformat(request.args.get('start_date').replace('Z', '+00:00'))
        
        if request.args.get('end_date'):
            from datetime import datetime
            end_date = datetime.fromisoformat(request.args.get('end_date').replace('Z', '+00:00'))
            
    except (ValueError, TypeError) as e:
        return jsonify({
            'error': {
                'code': 'INVALID_PARAMETERS',
                'message': f'Invalid date parameters: {str(e)}'
            }
        }), 400
    
    # Get summary through service
    service = get_expense_service()
    summary = service.get_expense_summary(start_date=start_date, end_date=end_date)
    
    # Serialize response
    result = summary_schema.dump(summary)
    
    return jsonify(result), 200