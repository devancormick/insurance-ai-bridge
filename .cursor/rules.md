# Cursor AI Rules for Insurance AI Bridge Project

## Project Context
This is a HIPAA-compliant healthcare insurance system. All code must prioritize:
1. Security and privacy
2. Type safety
3. Error handling
4. Audit logging

## Code Standards

### TypeScript/React
- Use TypeScript strict mode
- Prefer functional components with hooks
- Use React Query for data fetching
- Always handle loading and error states
- Add JSDoc comments for complex logic

### Python/FastAPI
- Use type hints everywhere
- Use Pydantic models for validation
- Async/await for all I/O operations
- Handle exceptions explicitly
- Add docstrings to all functions

### Security Requirements
- Never log PII (names, DOB, SSN)
- Always use parameterized queries
- Validate all inputs with Pydantic
- Use environment variables for secrets
- Implement rate limiting on all endpoints

### Testing Requirements
- Write tests for all business logic
- Mock external services in tests
- Test error paths, not just happy paths
- Aim for 80%+ code coverage

## Git Workflow
- Use semantic commit messages: [COMPONENT] Action: Description
- Keep commits focused and atomic
- Always run linters before committing
- Test locally before pushing

## When Adding New Features
1. Define Pydantic schema first
2. Write tests before implementation
3. Implement with proper error handling
4. Add logging and monitoring
5. Update documentation

