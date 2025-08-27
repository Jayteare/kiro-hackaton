"""
Marshmallow schemas for expense summary responses.
"""
from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from marshmallow.fields import DateTime


class CategorySummarySchema(Schema):
    """
    Schema for individual category summary within expense summary.
    """
    category = fields.String(
        required=True,
        metadata={"doc": "Category name"}
    )
    amount = fields.Decimal(
        required=True,
        places=2,
        as_string=True,
        metadata={"doc": "Total amount for this category"}
    )
    count = fields.Integer(
        required=True,
        validate=validate.Range(min=0),
        metadata={"doc": "Number of expenses in this category"}
    )


class DateRangeSchema(Schema):
    """
    Schema for date range information in summary.
    """
    start = DateTime(
        format='iso',
        allow_none=True,
        metadata={"doc": "Start date of the summary range (ISO format)"}
    )
    end = DateTime(
        format='iso', 
        allow_none=True,
        metadata={"doc": "End date of the summary range (ISO format)"}
    )


class SummarySchema(Schema):
    """
    Schema for expense summary responses.
    Provides aggregated information about expenses.
    """
    total_amount = fields.Decimal(
        required=True,
        places=2,
        as_string=True,
        validate=validate.Range(min=0),
        metadata={"doc": "Total amount of all expenses in the summary"}
    )
    expense_count = fields.Integer(
        required=True,
        validate=validate.Range(min=0),
        metadata={"doc": "Total number of expenses in the summary"}
    )
    date_range = fields.Nested(
        DateRangeSchema,
        required=True,
        metadata={"doc": "Date range for the summary"}
    )
    categories = fields.List(
        fields.Nested(CategorySummarySchema),
        required=True,
        metadata={"doc": "Summary breakdown by category"}
    )

    @validates('categories')
    def validate_categories(self, value):
        """Validate categories list."""
        if not isinstance(value, list):
            raise ValidationError("Categories must be a list")
        
        # Check for duplicate categories
        category_names = [cat.get('category') for cat in value if isinstance(cat, dict)]
        if len(category_names) != len(set(category_names)):
            raise ValidationError("Duplicate categories found in summary")


class SummaryRequestSchema(Schema):
    """
    Schema for expense summary request parameters.
    Used for validating query parameters for summary endpoints.
    """
    start_date = DateTime(
        format='iso',
        allow_none=True,
        metadata={"doc": "Start date for summary filtering (ISO format)"}
    )
    end_date = DateTime(
        format='iso',
        allow_none=True, 
        metadata={"doc": "End date for summary filtering (ISO format)"}
    )
    category = fields.String(
        validate=validate.Length(max=100),
        allow_none=True,
        metadata={"doc": "Filter summary by specific category"}
    )

    @validates('start_date')
    def validate_start_date(self, value):
        """Validate start date."""
        # Additional validation can be added here if needed
        pass

    @validates('end_date')
    def validate_end_date(self, value):
        """Validate end date."""
        # Additional validation can be added here if needed
        pass

    @validates_schema
    def validate_date_range(self, data, **kwargs):
        """Validate that start_date is before end_date if both are provided."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date must be before end date")