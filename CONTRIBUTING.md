# Contributing to Insurance AI Bridge

Thank you for your interest in contributing to the Insurance AI Bridge project!

## Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd insurance-ai-bridge
   ```

2. **Set up backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Set up frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Development Workflow

### Git Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following the project's style guide
   - Add tests for new features
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Backend tests
   cd backend
   pytest
   
   # Frontend tests
   cd frontend
   npm test
   npm run build
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "[COMPONENT] Action: Description"
   ```

5. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

Follow this format: `[COMPONENT] Action: Description`

**Components:**
- `[BACKEND]` - Backend application code
- `[FRONTEND]` - Frontend React components
- `[API]` - API endpoints and routes
- `[LLM]` - LLM integration
- `[SECURITY]` - Security features
- `[TEST]` - Test code
- `[DOCS]` - Documentation
- `[FIX]` - Bug fixes
- `[DEPLOY]` - Deployment configuration

**Examples:**
```
[BACKEND] Add user authentication endpoint
[FRONTEND] Create claim search component
[API] Implement rate limiting middleware
[TEST] Add integration tests for PII handler
[FIX] Resolve token refresh race condition
```

## Code Style

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints for all functions
- Maximum line length: 100 characters
- Use Black for code formatting: `black .`
- Use mypy for type checking: `mypy app/`
- Use ruff for linting: `ruff check .`

### TypeScript (Frontend)
- Use TypeScript strict mode
- Follow ESLint rules
- Use Prettier for formatting
- Maximum line length: 100 characters
- Prefer functional components with hooks

## Testing

### Backend Tests
```bash
cd backend
pytest                    # Run all tests
pytest tests/test_pii_handler.py -v  # Run specific test file
pytest --cov=app         # Run with coverage
```

### Frontend Tests
```bash
cd frontend
npm test                  # Run unit tests
npm run test:e2e         # Run E2E tests
npm run build            # Test build
```

## Security Guidelines

- **Never commit secrets** - Use environment variables
- **Never log PII** - All PII must be masked
- **Use parameterized queries** - Prevent SQL injection
- **Validate all inputs** - Use Pydantic schemas
- **Rate limit endpoints** - Prevent abuse
- **Follow HIPAA guidelines** - Maintain compliance

## Documentation

- Update README.md for major changes
- Add docstrings to all functions
- Update API documentation for endpoint changes
- Keep architecture diagrams current

## Questions?

For questions or concerns, please open an issue on GitHub or contact the maintainers.

