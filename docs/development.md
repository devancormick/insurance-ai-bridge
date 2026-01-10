# Development Guide

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or SQLite for development)
- Redis 7+ (optional, uses in-memory fallback)

### Quick Start

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   
   # Copy and configure environment
   cp ../.env.example ../.env
   # Edit .env with your settings
   
   # Run migrations (if using PostgreSQL)
   alembic upgrade head
   
   # Start development server
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   
   # Start development server
   npm run dev
   ```

3. **Access Applications**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Running Tests

### Backend Tests
```bash
cd backend
pytest                      # All tests
pytest -v                   # Verbose output
pytest --cov=app           # With coverage
pytest tests/test_pii_handler.py  # Specific test file
```

### Frontend Tests
```bash
cd frontend
npm test                    # Jest tests
npm run test:e2e           # Playwright E2E tests
```

## Database Migrations

### Create a new migration
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

## Code Quality

### Backend
```bash
# Format code
black app/ tests/

# Type checking
mypy app/

# Linting
ruff check app/
```

### Frontend
```bash
# Format code
npm run lint:fix

# Type checking
npm run type-check
```

## Adding New Features

1. **Backend API Endpoint**
   - Create endpoint in `app/api/v1/`
   - Add Pydantic schemas in `app/schemas/`
   - Write tests in `tests/`
   - Update API documentation

2. **Frontend Component**
   - Create component in `src/components/`
   - Add TypeScript types in `src/types/`
   - Create hooks in `src/hooks/` if needed
   - Add tests

3. **Database Changes**
   - Update model in `app/models/`
   - Create migration: `alembic revision --autogenerate`
   - Test migration

## Debugging

### Backend
- Use `logger.debug()` for detailed logging
- Enable debug mode: `DEBUG=true` in .env
- Use FastAPI's interactive docs at `/docs`

### Frontend
- Use React DevTools
- Check browser console for errors
- Use Next.js development mode for detailed errors

## Performance Optimization

### Backend
- Use caching for frequently accessed data
- Optimize database queries with indexes
- Use async/await for I/O operations
- Monitor with `/metrics` endpoint

### Frontend
- Use React Query caching
- Implement code splitting
- Optimize images and assets
- Use Next.js Image component

## Troubleshooting

### Common Issues

1. **Import errors**
   - Check Python path
   - Verify virtual environment is activated
   - Reinstall dependencies

2. **Database connection errors**
   - Verify DATABASE_URL in .env
   - Check PostgreSQL is running
   - Test connection manually

3. **Frontend build errors**
   - Clear .next directory: `rm -rf .next`
   - Reinstall node_modules: `rm -rf node_modules && npm install`
   - Check TypeScript errors

4. **Port already in use**
   - Change port in .env or config
   - Kill process using the port

