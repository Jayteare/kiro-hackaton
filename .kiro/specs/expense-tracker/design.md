# Design Document

## Overview

AppForge Demo is a Flask-based REST API microservice for expense tracking. The service follows a layered architecture with clear separation between API endpoints, business logic, and data persistence. The design prioritizes simplicity and rapid development while maintaining good practices for a hackathon environment.

## Architecture

The application follows a three-layer architecture:

```
┌─────────────────┐
│   API Layer     │  ← Flask routes, request/response handling
├─────────────────┤
│ Business Layer  │  ← Expense logic, validation, calculations
├─────────────────┤
│   Data Layer    │  ← SQLite database, data models
└─────────────────┘
```

### Technology Stack
- **Framework**: Flask with Flask-RESTful for API structure
- **Database**: SQLite for simplicity (file-based, no setup required)
- **ORM**: SQLAlchemy for database operations
- **Validation**: Marshmallow for request/response serialization
- **Testing**: pytest for unit tests

## Components and Interfaces

### API Endpoints

```
GET    /api/expenses           # List all expenses (with pagination)
POST   /api/expenses           # Create new expense
GET    /api/expenses/{id}      # Get specific expense
PUT    /api/expenses/{id}      # Update expense
DELETE /api/expenses/{id}      # Delete expense
GET    /api/expenses/summary   # Get expense summary
GET    /api/categories         # List available categories
GET    /health                 # Health check endpoint
```

### Core Components

#### 1. Expense Model
```python
class Expense:
    id: int (primary key)
    amount: decimal (required, positive)
    description: string (required, max 255 chars)
    category: string (default: "Uncategorized")
    date: datetime (default: current timestamp)
    created_at: datetime
    updated_at: datetime
```

#### 2. ExpenseService
- Handles business logic and validation
- Manages CRUD operations
- Calculates summaries and aggregations
- Enforces business rules

#### 3. ExpenseRepository
- Database access layer
- SQLAlchemy model definitions
- Query optimization for summaries

#### 4. API Controllers
- Request/response handling
- Input validation using Marshmallow schemas
- Error handling and HTTP status codes

## Data Models

### Expense Schema (Request/Response)
```json
{
  "id": 1,
  "amount": 25.50,
  "description": "Coffee and pastry",
  "category": "Food",
  "date": "2025-01-15T10:30:00Z",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### Summary Response Schema
```json
{
  "total_amount": 150.75,
  "expense_count": 12,
  "date_range": {
    "start": "2025-01-01T00:00:00Z",
    "end": "2025-01-31T23:59:59Z"
  },
  "categories": [
    {
      "category": "Food",
      "amount": 85.25,
      "count": 8
    },
    {
      "category": "Transport",
      "amount": 65.50,
      "count": 4
    }
  ]
}
```

### Database Schema
```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    description VARCHAR(255) NOT NULL,
    category VARCHAR(100) DEFAULT 'Uncategorized',
    date DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_expenses_date ON expenses(date);
CREATE INDEX idx_expenses_category ON expenses(category);
```

## Error Handling

### Standard Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "amount": ["Amount must be a positive number"]
    }
  }
}
```

### HTTP Status Codes
- `200 OK`: Successful GET, PUT operations
- `201 Created`: Successful POST operations
- `204 No Content`: Successful DELETE operations
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server errors

### Error Categories
1. **Validation Errors**: Invalid input format, missing required fields
2. **Business Logic Errors**: Negative amounts, invalid dates
3. **Resource Errors**: Expense not found, database connection issues
4. **System Errors**: Unexpected server errors

## Testing Strategy

### Unit Tests
- **Model Tests**: Validate expense model behavior and constraints
- **Service Tests**: Test business logic, validation, and calculations
- **Repository Tests**: Test database operations with in-memory SQLite
- **API Tests**: Test endpoint behavior, status codes, and response formats

### Test Data Strategy
- Use factory pattern for creating test expenses
- Separate test database (in-memory SQLite)
- Fixtures for common test scenarios

### Coverage Goals
- Aim for 80%+ code coverage
- Focus on critical business logic paths
- Test error conditions and edge cases

### Integration Testing
- Test complete request/response cycles
- Validate database persistence
- Test API contract compliance

## Performance Considerations

### Database Optimization
- Indexes on frequently queried fields (date, category)
- Pagination for large result sets
- Efficient summary queries using SQL aggregation

### Caching Strategy
- Simple in-memory caching for category lists
- Consider Redis for production scaling

### Resource Management
- Connection pooling for database
- Request timeout handling
- Memory-efficient pagination

## Security Considerations

### Input Validation
- Strict input validation using Marshmallow
- SQL injection prevention through SQLAlchemy ORM
- XSS prevention in API responses

### Basic Security Headers
- CORS configuration for cross-origin requests
- Content-Type validation
- Request size limits

## Deployment Architecture

### Development Setup
- Single Flask application
- SQLite database file
- Local development server

### Production Considerations
- WSGI server (Gunicorn) for production
- Environment-based configuration
- Database migration strategy
- Health check endpoint for monitoring

## Configuration Management

### Environment Variables
```
FLASK_ENV=development|production
DATABASE_URL=sqlite:///expenses.db
SECRET_KEY=your-secret-key
PAGINATION_SIZE=20
```

### Configuration Classes
- Development config (debug mode, local database)
- Production config (optimized settings, external database)
- Testing config (in-memory database, fast execution)