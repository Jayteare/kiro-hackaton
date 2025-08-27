"""
Marshmallow schemas for expense request/response validation and serialization.
"""
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError, post_load, EXCLUDE
from marshmallow.fields import DateTime


class ExpenseSchema(Schema):
    """
    Schema for expense serialization and deserialization.
    Used for complete expense representation in responses.
    """
    id = fields.Integer(dump_only=True, metadata={"doc": "Unique expense identifier"})
    amount = fields.Decimal(
        required=True,
        places=2,
        as_string=True,
        validate=validate.Range(min=Decimal('0.01'), error="Amount must be positive"),
        metadata={"doc": "Expense amount (positive decimal)"}
    )
    description = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=255, error="Description must be between 1 and 255 characters"),
            validate.Regexp(r'^(?!\s*$).+', error="Description cannot be empty or only whitespace")
        ],
        metadata={"doc": "Expense description"}
    )
    category = fields.String(
        load_default="Uncategorized",
        dump_default="Uncategorized",
        validate=validate.Length(max=100, error="Category must be 100 characters or less"),
        metadata={"doc": "Expense category"}
    )
    date = DateTime(
        load_default=lambda: datetime.now(timezone.utc),
        dump_default=lambda: datetime.now(timezone.utc),
        format='iso',
        metadata={"doc": "Date when expense occurred (ISO format)"}
    )
    created_at = DateTime(
        dump_only=True,
        format='iso',
        metadata={"doc": "Record creation timestamp"}
    )
    updated_at = DateTime(
        dump_only=True,
        format='iso',
        metadata={"doc": "Record last update timestamp"}
    )

    @validates('amount')
    def validate_amount(self, value):
        """Additional validation for amount field."""
        if value is None:
            raise ValidationError("Amount is required")
        
        try:
            # Ensure we can convert to Decimal
            decimal_value = Decimal(str(value))
            if decimal_value < Decimal('0.01'):
                raise ValidationError("Amount must be positive")
        except (InvalidOperation, ValueError):
            raise ValidationError("Amount must be a valid number")

    @validates('description')
    def validate_description(self, value):
        """Additional validation for description field."""
        if not value or not str(value).strip():
            raise ValidationError("Description cannot be empty")

    @validates('category')
    def validate_category(self, value):
        """Normalize category field."""
        if value and isinstance(value, str):
            value = value.strip()
            if not value:
                return "Uncategorized"
        return value or "Uncategorized"

    @post_load
    def normalize_data(self, data, **kwargs):
        """Normalize data after loading."""
        # Ensure category is set
        if not data.get('category') or not str(data.get('category')).strip():
            data['category'] = "Uncategorized"
        else:
            data['category'] = str(data['category']).strip()
        
        # Ensure description is trimmed
        if 'description' in data:
            data['description'] = str(data['description']).strip()
        
        return data


class ExpenseCreateSchema(Schema):
    """
    Schema for expense creation requests.
    Excludes read-only fields like id, created_at, updated_at.
    """
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields like id, created_at, updated_at
    amount = fields.Decimal(
        required=True,
        places=2,
        as_string=True,
        validate=validate.Range(min=Decimal('0.01'), error="Amount must be positive"),
        metadata={"doc": "Expense amount (positive decimal)"}
    )
    description = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=255, error="Description must be between 1 and 255 characters"),
            validate.Regexp(r'^(?!\s*$).+', error="Description cannot be empty or only whitespace")
        ],
        metadata={"doc": "Expense description"}
    )
    category = fields.String(
        load_default="Uncategorized",
        dump_default="Uncategorized",
        validate=validate.Length(max=100, error="Category must be 100 characters or less"),
        metadata={"doc": "Expense category"}
    )
    date = DateTime(
        load_default=lambda: datetime.now(timezone.utc),
        dump_default=lambda: datetime.now(timezone.utc),
        format='iso',
        metadata={"doc": "Date when expense occurred (ISO format)"}
    )

    @validates('amount')
    def validate_amount(self, value):
        """Additional validation for amount field."""
        if value is None:
            raise ValidationError("Amount is required")
        
        try:
            # Ensure we can convert to Decimal
            decimal_value = Decimal(str(value))
            if decimal_value <= 0:
                raise ValidationError("Amount must be positive")
        except (InvalidOperation, ValueError):
            raise ValidationError("Amount must be a valid number")

    @validates('description')
    def validate_description(self, value):
        """Additional validation for description field."""
        if not value or not str(value).strip():
            raise ValidationError("Description cannot be empty")

    @validates('category')
    def validate_category(self, value):
        """Normalize category field."""
        if value and isinstance(value, str):
            value = value.strip()
            if not value:
                return "Uncategorized"
        return value or "Uncategorized"

    @post_load
    def normalize_data(self, data, **kwargs):
        """Normalize data after loading."""
        # Ensure category is set
        if not data.get('category') or not str(data.get('category')).strip():
            data['category'] = "Uncategorized"
        else:
            data['category'] = str(data['category']).strip()
        
        # Ensure description is trimmed
        if 'description' in data:
            data['description'] = str(data['description']).strip()
        
        return data


class ExpenseUpdateSchema(Schema):
    """
    Schema for expense update requests.
    All fields are optional for partial updates.
    """
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields like id, created_at, updated_at
    amount = fields.Decimal(
        places=2,
        as_string=True,
        validate=validate.Range(min=Decimal('0.01'), error="Amount must be positive"),
        metadata={"doc": "Expense amount (positive decimal)"}
    )
    description = fields.String(
        validate=[
            validate.Length(min=1, max=255, error="Description must be between 1 and 255 characters"),
            validate.Regexp(r'^(?!\s*$).+', error="Description cannot be empty or only whitespace")
        ],
        metadata={"doc": "Expense description"}
    )
    category = fields.String(
        validate=validate.Length(max=100, error="Category must be 100 characters or less"),
        metadata={"doc": "Expense category"}
    )
    date = DateTime(
        format='iso',
        metadata={"doc": "Date when expense occurred (ISO format)"}
    )

    @validates('amount')
    def validate_amount(self, value):
        """Additional validation for amount field."""
        if value is not None:
            try:
                decimal_value = Decimal(str(value))
                if decimal_value <= 0:
                    raise ValidationError("Amount must be positive")
            except (InvalidOperation, ValueError):
                raise ValidationError("Amount must be a valid number")

    @validates('description')
    def validate_description(self, value):
        """Additional validation for description field."""
        if value is not None and (not value or not str(value).strip()):
            raise ValidationError("Description cannot be empty")

    @validates_schema
    def validate_schema(self, data, **kwargs):
        """Validate that at least one field is provided for update."""
        if not data:
            raise ValidationError("At least one field must be provided for update")

    @post_load
    def normalize_data(self, data, **kwargs):
        """Normalize data after loading."""
        # Normalize category if provided
        if 'category' in data:
            if not data['category'] or not str(data['category']).strip():
                data['category'] = "Uncategorized"
            else:
                data['category'] = str(data['category']).strip()
        
        # Ensure description is trimmed if provided
        if 'description' in data and data['description'] is not None:
            data['description'] = str(data['description']).strip()
        
        return data


class CategorySummarySchema(Schema):
    """
    Schema for individual category summary in expense summary response.
    """
    category = fields.String(
        required=True,
        metadata={"doc": "Category name"}
    )
    amount = fields.Float(
        required=True,
        metadata={"doc": "Total amount for this category"}
    )
    count = fields.Integer(
        required=True,
        metadata={"doc": "Number of expenses in this category"}
    )


class DateRangeSchema(Schema):
    """
    Schema for date range in summary response.
    """
    start = fields.String(
        allow_none=True,
        metadata={"doc": "Start date of the range (ISO format)"}
    )
    end = fields.String(
        allow_none=True,
        metadata={"doc": "End date of the range (ISO format)"}
    )


class ExpenseSummarySchema(Schema):
    """
    Schema for expense summary response.
    """
    total_amount = fields.Float(
        required=True,
        metadata={"doc": "Total amount of all expenses"}
    )
    expense_count = fields.Integer(
        required=True,
        metadata={"doc": "Total number of expenses"}
    )
    date_range = fields.Nested(
        DateRangeSchema,
        required=True,
        metadata={"doc": "Date range for the summary"}
    )
    categories = fields.List(
        fields.Nested(CategorySummarySchema),
        required=True,
        metadata={"doc": "Category breakdown of expenses"}
    )