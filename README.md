# Insurance AI Bridge System

**Project Name:** Insurance AI Bridge System  

## Project Overview

### Problem Statement
Legacy insurance portals trap valuable data in unstructured free-text formats across disconnected screens, costing $40K/month in manual overhead. Staff spend 15-20 minutes per case hunting for context that exists but isn't actionable.

### Solution
Build an intelligent bridge layer that sits on top of existing systems without touching core logic, using LLMs to structure and contextualize data in real-time.

### Key Objectives
- Reduce case research time from 18 minutes to <2 minutes
- Cut monthly labor costs by 67% ($40K → $12K)
- Maintain HIPAA compliance with zero-retention PII handling
- Improve staff satisfaction and reduce errors
- Avoid risky $500K+ core system rewrites

## Technology Stack

### Frontend
- **Framework:** Next.js 14.x (App Router)
- **Language:** TypeScript 5.x
- **Styling:** Tailwind CSS 3.x
- **State Management:** React Query + Zustand
- **HTTP Client:** Axios

### Backend
- **Framework:** FastAPI 0.104.x
- **Language:** Python 3.11+
- **Validation:** Pydantic 2.x
- **Database Access:** SQLAlchemy 2.x (async)
- **LLM Integration:** OpenAI Python SDK / Anthropic SDK

### Infrastructure
- **Database:** PostgreSQL 15+ (read replicas from SQL Server)
- **Caching:** Redis 7.x
- **Containerization:** Docker & Docker Compose

## Quick Start

### Prerequisites
- Node.js 18+ and npm 9+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

### Setup

1. **Clone and navigate to project:**
   ```bash
   cd insurance-ai-bridge
   ```

2. **Run setup script:**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

4. **Start development environment:**
   ```bash
   docker-compose up -d
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Project Structure

```
insurance-ai-bridge/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── scripts/           # Utility scripts
├── docs/              # Documentation
└── .cursor/           # Cursor AI configuration
```

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate  # or venv/Scripts/activate on Windows
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Git Workflow Setup

We use **GitHub Flow** with feature branches, a `staging` branch for testing, and `main` for production.

**Quick Start:**
```bash
# Setup Git workflow (creates staging branch)
./scripts/setup_git_workflow.sh

# Install Git hooks (enforces commit message format and code quality)
./scripts/setup_git_hooks.sh

# Create a feature branch
./scripts/create_feature_branch.sh ISSUE-123 add-user-authentication
```

**For detailed workflow instructions, see:**
- [Git Workflow Guide](docs/git-workflow.md) - Complete Git workflow documentation
- [Contributing Guidelines](CONTRIBUTING.md) - Development workflow and best practices
- [Branch Protection Setup](.github/BRANCH_PROTECTION_SETUP.md) - Branch protection configuration

## Security & HIPAA Compliance

This system is designed with HIPAA compliance in mind:
- Zero-retention PII policy for LLM calls
- PII tokenization before external API calls
- Comprehensive audit logging
- Encryption at rest and in transit
- Role-based access control

## Documentation

- [Architecture Documentation](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Security Guidelines](docs/security.md)
- [Deployment Guide](docs/deployment.md)
- [Git Workflow Guide](docs/git-workflow.md) - Complete Git workflow and branching strategy
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute to the project

## License

Proprietary - Internal Use Only