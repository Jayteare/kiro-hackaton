"""
Expense service layer containing business logic and validation.
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from decimal import Decimal, InvalidOperation
from sqlalchemy.orm import Session
from app.models.expense import Expense
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.expense_schema import ExpenseCreateSchema, ExpenseUpdateSchema, ExpenseSchema


class ExpenseServiceError(Exception):
    """Base exception for expense service errors."""
    pass


class ValidationError(ExpenseServiceError):
    """Exception raised for validation errors."""
    pass


class NotFoundError(ExpenseServiceError):
    """Exception raised when expense is not found."""
    pass


class ExpenseService:
    """
    Service class for expense business logic and validation.
    
    This class handles all business rules, validation, and orchestrates
    interactions between the repository layer and API layer.
    """
    
    def __init__(self, session: Session):
        """
        Initialize service with database session.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
        self.repository = ExpenseRepository(session)
        self.create_schema = ExpenseCreateSchema()
        self.update_schema = ExpenseUpdateSchema()
        self.response_schema = ExpenseSchema()
    
    def create_expense(self, expense_data: Dict[str, Any]) -> Expense:
        """
        Create a new expense with validation and business rules.
        
        Args:
            expense_data: Dictionary containing expense data
            
        Returns:
            Created expense object
            
        Raises:
            ValidationError: If validation fails
            ExpenseServiceError: If creation fails
        """
        try:
            # Validate input data using schema
            validated_data = self.create_schema.load(expense_data)
            
            # Apply business rules
            validated_data = self._apply_creation_business_rules(validated_data)
            
            # Create expense through repository
            expense = self.repository.create(validated_data)
            
            return expense
            
        except Exception as e:
            if hasattr(e, 'messages'):
                # Marshmallow validation error
                raise ValidationError(f"Validation failed: {e.messages}")
            elif isinstance(e, ValueError):
                # Model validation error
                raise ValidationError(str(e))
            else:
                # Other errors
                raise ExpenseServiceError(f"Failed to create expense: {str(e)}")
    
    def get_expense(self, expense_id: int) -> Expense:
        """
        Get expense by ID with validation.
        
        Args:
            expense_id: Expense ID to retrieve
            
        Returns:
            Expense object
            
        Raises:
            ValidationError: If expense_id is invalid
            NotFoundError: If expense is not found
        """
        if not isinstance(expense_id, int) or expense_id <= 0:
            raise ValidationError("Expense ID must be a positive integer")
        
        expense = self.repository.get_by_id(expense_id)
        if not expense:
            raise NotFoundError(f"Expense with ID {expense_id} not found")
        
        return expense
    
    def get_expenses(self, 
                    page: int = 1, 
                    per_page: int = 20,
                    category: Optional[str] = None,
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None,
                    sort_by: str = 'date',
                    sort_order: str = 'desc') -> Tuple[List[Expense], int]:
        """
        Get expenses with filtering, pagination, and validation.
        
        Args:
            page: Page number (1-based)
            per_page: Number of items per page
            category: Filter by category (optional)
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            
        Returns:
            Tuple of (expenses list, total count)
            
        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate pagination parameters
        if not isinstance(page, int) or page < 1:
            raise ValidationError("Page must be a positive integer")
        
        if not isinstance(per_page, int) or per_page < 1 or per_page > 100:
            raise ValidationError("Per page must be between 1 and 100")
        
        # Validate sort parameters
        valid_sort_fields = ['date', 'amount', 'category', 'created_at']
        if sort_by not in valid_sort_fields:
            raise ValidationError(f"Sort field must be one of: {', '.join(valid_sort_fields)}")
        
        if sort_order.lower() not in ['asc', 'desc']:
            raise ValidationError("Sort order must be 'asc' or 'desc'")
        
        # Validate date range
        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date must be before or equal to end date")
        
        # Validate category
        if category is not None:
            category = str(category).strip()
            if not category:
                category = None
        
        try:
            return self.repository.get_all(
                page=page,
                per_page=per_page,
                category=category,
                start_date=start_date,
                end_date=end_date,
                sort_by=sort_by,
                sort_order=sort_order
            )
        except Exception as e:
            raise ExpenseServiceError(f"Failed to retrieve expenses: {str(e)}")
    
    def update_expense(self, expense_id: int, update_data: Dict[str, Any]) -> Expense:
        """
        Update an existing expense with validation and business rules.
        
        Args:
            expense_id: ID of expense to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Updated expense object
            
        Raises:
            ValidationError: If validation fails
            NotFoundError: If expense is not found
            ExpenseServiceError: If update fails
        """
        if not isinstance(expense_id, int) or expense_id <= 0:
            raise ValidationError("Expense ID must be a positive integer")
        
        try:
            # Validate input data using schema
            validated_data = self.update_schema.load(update_data)
            
            # Apply business rules
            validated_data = self._apply_update_business_rules(validated_data)
            
            # Update expense through repository
            expense = self.repository.update(expense_id, validated_data)
            
            if not expense:
                raise NotFoundError(f"Expense with ID {expense_id} not found")
            
            return expense
            
        except Exception as e:
            if hasattr(e, 'messages'):
                # Marshmallow validation error
                raise ValidationError(f"Validation failed: {e.messages}")
            elif isinstance(e, ValueError):
                # Model validation error
                raise ValidationError(str(e))
            elif isinstance(e, NotFoundError):
                # Re-raise NotFoundError
                raise e
            else:
                # Other errors
                raise ExpenseServiceError(f"Failed to update expense: {str(e)}")
    
    def delete_expense(self, expense_id: int) -> bool:
        """
        Delete an expense with validation.
        
        Args:
            expense_id: ID of expense to delete
            
        Returns:
            True if expense was deleted
            
        Raises:
            ValidationError: If expense_id is invalid
            NotFoundError: If expense is not found
            ExpenseServiceError: If deletion fails
        """
        if not isinstance(expense_id, int) or expense_id <= 0:
            raise ValidationError("Expense ID must be a positive integer")
        
        try:
            deleted = self.repository.delete(expense_id)
            
            if not deleted:
                raise NotFoundError(f"Expense with ID {expense_id} not found")
            
            return True
            
        except NotFoundError:
            # Re-raise NotFoundError
            raise
        except Exception as e:
            raise ExpenseServiceError(f"Failed to delete expense: {str(e)}")
    
    def get_categories(self) -> List[str]:
        """
        Get all unique categories from expenses.
        
        Returns:
            List of unique category names
            
        Raises:
            ExpenseServiceError: If retrieval fails
        """
        try:
            categories = self.repository.get_categories()
            
            # Ensure "Uncategorized" is always included if there are any expenses
            if categories and "Uncategorized" not in categories:
                categories.append("Uncategorized")
            
            return sorted(categories)
            
        except Exception as e:
            raise ExpenseServiceError(f"Failed to retrieve categories: {str(e)}")
    
    def get_expense_summary(self, 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get expense summary with category breakdown and validation.
        
        Args:
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
            
        Returns:
            Dictionary containing summary data
            
        Raises:
            ValidationError: If date parameters are invalid
            ExpenseServiceError: If summary generation fails
        """
        # Validate date range
        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date must be before or equal to end date")
        
        try:
            summary = self.repository.get_summary(start_date, end_date)
            
            # Apply business rules to summary
            summary = self._apply_summary_business_rules(summary)
            
            return summary
            
        except Exception as e:
            raise ExpenseServiceError(f"Failed to generate expense summary: {str(e)}")
    
    def _apply_creation_business_rules(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply business rules for expense creation.
        
        Args:
            expense_data: Validated expense data
            
        Returns:
            Expense data with business rules applied
        """
        # Ensure category is properly set
        if not expense_data.get('category') or not expense_data['category'].strip():
            expense_data['category'] = "Uncategorized"
        else:
            expense_data['category'] = expense_data['category'].strip().title()
        
        # Ensure description is trimmed
        if 'description' in expense_data:
            expense_data['description'] = expense_data['description'].strip()
        
        # Validate amount precision (business rule: max 2 decimal places)
        if 'amount' in expense_data:
            try:
                amount = Decimal(str(expense_data['amount']))
                # Round to 2 decimal places
                expense_data['amount'] = amount.quantize(Decimal('0.01'))
            except (InvalidOperation, ValueError):
                raise ValidationError("Invalid amount format")
        
        return expense_data
    
    def _apply_update_business_rules(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply business rules for expense updates.
        
        Args:
            expense_data: Validated expense data
            
        Returns:
            Expense data with business rules applied
        """
        # Apply same rules as creation for provided fields
        if 'category' in expense_data:
            if not expense_data['category'] or not expense_data['category'].strip():
                expense_data['category'] = "Uncategorized"
            else:
                expense_data['category'] = expense_data['category'].strip().title()
        
        if 'description' in expense_data:
            expense_data['description'] = expense_data['description'].strip()
        
        if 'amount' in expense_data:
            try:
                amount = Decimal(str(expense_data['amount']))
                expense_data['amount'] = amount.quantize(Decimal('0.01'))
            except (InvalidOperation, ValueError):
                raise ValidationError("Invalid amount format")
        
        return expense_data
    
    def _apply_summary_business_rules(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply business rules to expense summary.
        
        Args:
            summary: Raw summary data
            
        Returns:
            Summary data with business rules applied
        """
        # Ensure amounts are properly formatted with proper rounding
        if 'total_amount' in summary:
            # Use Decimal for precise rounding
            from decimal import Decimal, ROUND_HALF_UP
            amount = Decimal(str(summary['total_amount']))
            summary['total_amount'] = float(amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        
        # Format category amounts
        if 'categories' in summary:
            for category in summary['categories']:
                if 'amount' in category:
                    from decimal import Decimal, ROUND_HALF_UP
                    amount = Decimal(str(category['amount']))
                    category['amount'] = float(amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        
        return summary