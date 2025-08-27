"""
Expense repository for database operations.
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_, func
from app.models.expense import Expense


class ExpenseRepository:
    """Repository class for expense database operations."""
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
    
    def create(self, expense_data: Dict[str, Any]) -> Expense:
        """
        Create a new expense record.
        
        Args:
            expense_data: Dictionary containing expense data
            
        Returns:
            Created expense object
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            expense = Expense(**expense_data)
            self.session.add(expense)
            self.session.commit()
            self.session.refresh(expense)
            return expense
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_by_id(self, expense_id: int) -> Optional[Expense]:
        """
        Get expense by ID.
        
        Args:
            expense_id: Expense ID to retrieve
            
        Returns:
            Expense object if found, None otherwise
        """
        return self.session.query(Expense).filter(Expense.id == expense_id).first()
    
    def get_all(self, 
                page: int = 1, 
                per_page: int = 20,
                category: Optional[str] = None,
                start_date: Optional[datetime] = None,
                end_date: Optional[datetime] = None,
                sort_by: str = 'date',
                sort_order: str = 'desc') -> Tuple[List[Expense], int]:
        """
        Get all expenses with filtering and pagination.
        
        Args:
            page: Page number (1-based)
            per_page: Number of items per page
            category: Filter by category (optional)
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
            sort_by: Field to sort by ('date', 'amount', 'category', 'created_at')
            sort_order: Sort order ('asc' or 'desc')
            
        Returns:
            Tuple of (expenses list, total count)
        """
        query = self.session.query(Expense)
        
        # Apply filters
        filters = []
        
        if category:
            filters.append(Expense.category == category)
        
        if start_date:
            filters.append(Expense.date >= start_date)
            
        if end_date:
            filters.append(Expense.date <= end_date)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply sorting
        sort_column = getattr(Expense, sort_by, Expense.date)
        if sort_order.lower() == 'asc':
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
        
        # Apply pagination
        offset = (page - 1) * per_page
        expenses = query.offset(offset).limit(per_page).all()
        
        return expenses, total_count
    
    def update(self, expense_id: int, update_data: Dict[str, Any]) -> Optional[Expense]:
        """
        Update an existing expense.
        
        Args:
            expense_id: ID of expense to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Updated expense object if found, None otherwise
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            expense = self.get_by_id(expense_id)
            if not expense:
                return None
            
            # Update only provided fields
            for key, value in update_data.items():
                if hasattr(expense, key):
                    setattr(expense, key, value)
            
            # Update timestamp
            expense.updated_at = datetime.utcnow()
            
            self.session.commit()
            self.session.refresh(expense)
            return expense
        except Exception as e:
            self.session.rollback()
            raise e
    
    def delete(self, expense_id: int) -> bool:
        """
        Delete an expense by ID.
        
        Args:
            expense_id: ID of expense to delete
            
        Returns:
            True if expense was deleted, False if not found
            
        Raises:
            Exception: If database operation fails
        """
        try:
            expense = self.get_by_id(expense_id)
            if not expense:
                return False
            
            self.session.delete(expense)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_categories(self) -> List[str]:
        """
        Get all unique categories from expenses.
        
        Returns:
            List of unique category names
        """
        categories = self.session.query(Expense.category).distinct().all()
        return [category[0] for category in categories]
    
    def get_summary(self, 
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get expense summary with category breakdown.
        
        Args:
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
            
        Returns:
            Dictionary containing summary data
        """
        query = self.session.query(Expense)
        
        # Apply date filters
        filters = []
        if start_date:
            filters.append(Expense.date >= start_date)
        if end_date:
            filters.append(Expense.date <= end_date)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Get total amount and count
        total_result = query.with_entities(
            func.sum(Expense.amount).label('total_amount'),
            func.count(Expense.id).label('total_count')
        ).first()
        
        total_amount = float(total_result.total_amount) if total_result.total_amount else 0.0
        total_count = total_result.total_count if total_result.total_count else 0
        
        # Get category breakdown
        category_query = query.with_entities(
            Expense.category,
            func.sum(Expense.amount).label('category_amount'),
            func.count(Expense.id).label('category_count')
        ).group_by(Expense.category)
        
        categories = []
        for category_result in category_query.all():
            categories.append({
                'category': category_result.category,
                'amount': float(category_result.category_amount),
                'count': category_result.category_count
            })
        
        # Sort categories by amount (descending)
        categories.sort(key=lambda x: x['amount'], reverse=True)
        
        return {
            'total_amount': total_amount,
            'expense_count': total_count,
            'date_range': {
                'start': start_date.isoformat() if start_date else None,
                'end': end_date.isoformat() if end_date else None
            },
            'categories': categories
        }
    
    def exists(self, expense_id: int) -> bool:
        """
        Check if expense exists by ID.
        
        Args:
            expense_id: Expense ID to check
            
        Returns:
            True if expense exists, False otherwise
        """
        return self.session.query(Expense).filter(Expense.id == expense_id).first() is not None
    
    def count(self, 
              category: Optional[str] = None,
              start_date: Optional[datetime] = None,
              end_date: Optional[datetime] = None) -> int:
        """
        Count expenses with optional filters.
        
        Args:
            category: Filter by category (optional)
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
            
        Returns:
            Number of expenses matching filters
        """
        query = self.session.query(Expense)
        
        filters = []
        if category:
            filters.append(Expense.category == category)
        if start_date:
            filters.append(Expense.date >= start_date)
        if end_date:
            filters.append(Expense.date <= end_date)
        
        if filters:
            query = query.filter(and_(*filters))
        
        return query.count()