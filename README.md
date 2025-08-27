# Expense Tracker API

A Flask-based REST API microservice for personal expense tracking, built as part of the AppForge Demo hackathon project. This service provides comprehensive expense management capabilities with categorization, filtering, and reporting features.

## Features

- **Expense Management**: Create, read, update, and delete expense records
- **Categorization**: Organize expenses by category with automatic "Uncategorized" fallback
- **Filtering & Sorting**: Filter by category, date range, and sort by various fields
- **Pagination**: Efficient pagination for large datasets
- **Reporting**: Generate expense summaries with category breakdowns
- **Validation**: Comprehensive input validation and error handling
- **Performance**: Optimized database queries with indexing

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd kiro-hackaton
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python -m flask init-db
   ```

4. **Start the development server**
   ```bash
   python run.py
   ```

The API will be available at `http://127.0.0.1:5000`

### Environment Configuration

Create a `.env` file in the project root for custom configuration:

```env
FLASK_ENV=development
DATABASE_URL=sqlite:///expenses_dev.db
SECRET_KEY=your-secret-key-here
PAGINATION_SIZE=20
MAX_CONTENT_LENGTH=16777216
```

## API Documentation

### Base URL
```
http://127.0.0.1:5000
```

### Authentication
This API currently does not require authentication (hackathon prototype).

### Content Type
All requests and responses use `application/json`.

### Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      "field": ["Specific validation error"]
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

## Endpoints

### Health Check

#### GET /health
Check service health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "expense-tracker",
  "version": "1.0.0"
}
```

### Application Info

#### GET /
Get application information and available endpoints.

**Response:**
```json
{
  "service": "expense-tracker",
  "version": "1.0.0",
  "description": "Expense tracking microservice API",
  "endpoints": {
    "health": "/health",
    "api_health": "/api/health",
    "expenses": "/api/expenses",
    "categories": "/api/categories",
    "summary": "/api/expenses/summary"
  }
}
```

### Expenses

#### POST /api/expenses
Create a new expense.

**Request Body:**
```json
{
  "amount": "25.50",
  "description": "Coffee and pastry",
  "category": "Food",
  "date": "2025-01-15T10:30:00Z"
}
```

**Required Fields:**
- `amount`: Positive decimal number (string format)
- `description`: Non-empty string (max 255 characters)

**Optional Fields:**
- `category`: String (max 100 characters, defaults to "Uncategorized")
- `date`: ISO 8601 datetime string (defaults to current time)

**Response (201 Created):**
```json
{
  "id": 1,
  "amount": "25.50",
  "description": "Coffee and pastry",
  "category": "Food",
  "date": "2025-01-15T10:30:00Z",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

#### GET /api/expenses
List all expenses with pagination, filtering, and sorting.

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)
- `category`: Filter by category name
- `start_date`: Filter expenses from this date (ISO 8601)
- `end_date`: Filter expenses until this date (ISO 8601)
- `sort_by`: Sort field (`amount`, `date`, `category`, `description`)
- `sort_order`: Sort direction (`asc`, `desc`, default: `desc` for date)

**Examples:**
```bash
# Get first page with default pagination
GET /api/expenses

# Get specific page with custom page size
GET /api/expenses?page=2&per_page=10

# Filter by category
GET /api/expenses?category=Food

# Filter by date range
GET /api/expenses?start_date=2025-01-01T00:00:00Z&end_date=2025-01-31T23:59:59Z

# Sort by amount ascending
GET /api/expenses?sort_by=amount&sort_order=asc

# Combined filtering and sorting
GET /api/expenses?category=Food&sort_by=date&sort_order=desc&page=1&per_page=5
```

**Response (200 OK):**
```json
{
  "expenses": [
    {
      "id": 1,
      "amount": "25.50",
      "description": "Coffee and pastry",
      "category": "Food",
      "date": "2025-01-15T10:30:00Z",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_count": 1,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

#### GET /api/expenses/{id}
Get a specific expense by ID.

**Response (200 OK):**
```json
{
  "id": 1,
  "amount": "25.50",
  "description": "Coffee and pastry",
  "category": "Food",
  "date": "2025-01-15T10:30:00Z",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

#### PUT /api/expenses/{id}
Update an existing expense (partial updates supported).

**Request Body (all fields optional):**
```json
{
  "amount": "30.00",
  "description": "Updated coffee and pastry",
  "category": "Food & Drinks"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "amount": "30.00",
  "description": "Updated coffee and pastry",
  "category": "Food & Drinks",
  "date": "2025-01-15T10:30:00Z",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:35:00Z"
}
```

#### DELETE /api/expenses/{id}
Delete an expense.

**Response (204 No Content):**
No response body.

### Categories

#### GET /api/categories
List all available expense categories.

**Response (200 OK):**
```json
{
  "categories": [
    "Entertainment",
    "Food",
    "Shopping",
    "Transport",
    "Uncategorized",
    "Utilities"
  ]
}
```

### Summary & Reporting

#### GET /api/expenses/summary
Get expense summary with category breakdown.

**Query Parameters:**
- `start_date`: Include expenses from this date (ISO 8601)
- `end_date`: Include expenses until this date (ISO 8601)

**Examples:**
```bash
# Overall summary
GET /api/expenses/summary

# Summary for specific date range
GET /api/expenses/summary?start_date=2025-01-01T00:00:00Z&end_date=2025-01-31T23:59:59Z
```

**Response (200 OK):**
```json
{
  "total_amount": "150.75",
  "expense_count": 12,
  "date_range": {
    "start": "2025-01-01T00:00:00Z",
    "end": "2025-01-31T23:59:59Z"
  },
  "categories": [
    {
      "category": "Food",
      "amount": "85.25",
      "count": 8
    },
    {
      "category": "Transport",
      "amount": "65.50",
      "count": 4
    }
  ]
}
```

## Development

### Project Structure
```
kiro-hackaton/
├── app/                    # Application package
│   ├── api/               # API blueprints and routes
│   ├── models/            # Database models
│   ├── repositories/      # Data access layer
│   ├── schemas/           # Marshmallow schemas
│   ├── services/          # Business logic layer
│   └── __init__.py        # Application factory
├── tests/                 # Test suite
│   ├── fixtures.py        # Test fixtures and factories
│   ├── test_*.py         # Test modules
│   └── conftest.py       # Pytest configuration
├── scripts/              # Utility scripts
├── logs/                 # Application logs
├── config.py             # Configuration classes
├── run.py                # Application entry point
└── requirements.txt      # Python dependencies
```

### Running Tests

**Run all tests:**
```bash
pytest
```

**Run specific test categories:**
```bash
# Unit tests only
pytest tests/test_expense_model.py tests/test_expense_service.py

# API integration tests
pytest tests/test_expense_api.py

# End-to-end scenarios
pytest tests/test_end_to_end_scenarios.py

# Performance tests
pytest tests/test_performance.py

# Run with coverage
pytest --cov=app --cov-report=html
```

**Test with different configurations:**
```bash
# Test with verbose output
pytest -v

# Test specific function
pytest tests/test_expense_api.py::TestExpenseCreation::test_create_valid_expense

# Test with custom database
DATABASE_URL=sqlite:///test_custom.db pytest
```

### Database Management

**Initialize database:**
```bash
python -m flask init-db
```

**Reset database (drop and recreate):**
```bash
python -m flask reset-db
```

**Check current configuration:**
```bash
python -m flask check-config
```

### Configuration Environments

The application supports three environments:

1. **Development** (`FLASK_ENV=development`)
   - Debug mode enabled
   - SQL query logging
   - Pretty-printed JSON responses
   - File-based SQLite database

2. **Testing** (`FLASK_ENV=testing`)
   - In-memory SQLite database
   - Optimized for test performance
   - Reduced logging

3. **Production** (`FLASK_ENV=production`)
   - Debug mode disabled
   - Security headers enabled
   - Optimized performance settings
   - File-based logging with rotation

### Performance Considerations

- **Database Indexes**: Automatic indexes on `date` and `category` fields
- **Pagination**: Default page size of 20, maximum of 100
- **Query Optimization**: Efficient aggregation queries for summaries
- **Memory Management**: Streaming responses for large datasets
- **Caching**: Consider Redis for production scaling

### Security Features

- **Input Validation**: Comprehensive validation using Marshmallow schemas
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **Request Size Limits**: Configurable maximum request payload size
- **Error Handling**: Consistent error responses without sensitive information
- **CORS Support**: Configurable cross-origin request handling

## Deployment

### Local Development
```bash
python run.py
```

### Production Deployment

1. **Set environment variables:**
   ```bash
   export FLASK_ENV=production
   export DATABASE_URL=sqlite:///expenses.db
   export SECRET_KEY=your-production-secret-key
   ```

2. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 run:app
   ```

3. **Set up reverse proxy (nginx example):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Docker Deployment

A `Dockerfile` is included for containerized deployment:

```bash
# Build image
docker build -t expense-tracker .

# Run container
docker run -p 5000:5000 -e FLASK_ENV=production expense-tracker
```

### Cloud Deployment

The project includes scripts for Google Cloud Run deployment:

```bash
# Setup GCP resources
./scripts/setup-gcp-resources.bat

# Deploy to Cloud Run
./scripts/deploy-to-cloudrun.bat
```

## API Examples

### cURL Examples

**Create an expense:**
```bash
curl -X POST http://127.0.0.1:5000/api/expenses \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "25.50",
    "description": "Coffee and pastry",
    "category": "Food"
  }'
```

**Get expenses with filtering:**
```bash
curl "http://127.0.0.1:5000/api/expenses?category=Food&page=1&per_page=5"
```

**Update an expense:**
```bash
curl -X PUT http://127.0.0.1:5000/api/expenses/1 \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "30.00",
    "description": "Updated description"
  }'
```

**Get expense summary:**
```bash
curl "http://127.0.0.1:5000/api/expenses/summary?start_date=2025-01-01T00:00:00Z"
```

### Python Client Example

```python
import requests
import json

# Base URL
base_url = "http://127.0.0.1:5000/api"

# Create an expense
expense_data = {
    "amount": "25.50",
    "description": "Coffee and pastry",
    "category": "Food"
}

response = requests.post(f"{base_url}/expenses", json=expense_data)
expense = response.json()
print(f"Created expense with ID: {expense['id']}")

# Get all expenses
response = requests.get(f"{base_url}/expenses")
expenses = response.json()
print(f"Total expenses: {expenses['pagination']['total_count']}")

# Get summary
response = requests.get(f"{base_url}/expenses/summary")
summary = response.json()
print(f"Total amount: ${summary['total_amount']}")
```

### JavaScript/Fetch Example

```javascript
const baseUrl = 'http://127.0.0.1:5000/api';

// Create an expense
async function createExpense() {
  const expenseData = {
    amount: '25.50',
    description: 'Coffee and pastry',
    category: 'Food'
  };
  
  const response = await fetch(`${baseUrl}/expenses`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(expenseData)
  });
  
  const expense = await response.json();
  console.log('Created expense:', expense);
}

// Get expenses with filtering
async function getExpenses() {
  const response = await fetch(`${baseUrl}/expenses?category=Food&page=1&per_page=10`);
  const data = await response.json();
  console.log('Expenses:', data.expenses);
  console.log('Pagination:', data.pagination);
}
```

## Troubleshooting

### Common Issues

1. **Database not found error**
   ```bash
   # Initialize the database
   python -m flask init-db
   ```

2. **Port already in use**
   ```bash
   # Use a different port
   PORT=5001 python run.py
   ```

3. **Import errors**
   ```bash
   # Ensure you're in the project directory and dependencies are installed
   pip install -r requirements.txt
   ```

4. **Test failures**
   ```bash
   # Reset test database
   FLASK_ENV=testing python -m flask reset-db
   pytest
   ```

### Logging

Logs are written to:
- **Development**: Console output
- **Production**: `logs/expense_tracker.log` with rotation

Enable debug logging:
```bash
FLASK_ENV=development python run.py
```

### Performance Issues

If experiencing slow responses:

1. Check database indexes are created
2. Reduce pagination page size
3. Use date range filters for summaries
4. Monitor log files for slow queries

## Contributing

This is a hackathon project focused on rapid prototyping. For production use, consider:

- Adding authentication and authorization
- Implementing rate limiting
- Adding comprehensive monitoring
- Setting up automated backups
- Implementing data validation at database level
- Adding API versioning
- Implementing caching strategies

## License

This project is part of a hackathon demonstration and is provided as-is for educational purposes.