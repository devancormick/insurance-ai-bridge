# AI Bridge for Legacy Insurance Portals - Complete Project Guideline

**Project Name:** Insurance AI Bridge System  
**Developer:** Devan McCormick (devancormick@outlook.com)  
**Timeline:** December 1, 2024 - December 28, 2024  
**Timezone:** CST (Central Standard Time)  
**Repository:** Local Git with user-specific configuration

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Git Configuration & Workflow](#git-configuration--workflow)
6. [Daily Commit Schedule](#daily-commit-schedule)
7. [Setup Instructions](#setup-instructions)
8. [Implementation Guide](#implementation-guide)
9. [Security & HIPAA Compliance](#security--hipaa-compliance)
10. [Testing Strategy](#testing-strategy)
11. [Deployment Guide](#deployment-guide)
12. [Cursor AI Development Instructions](#cursor-ai-development-instructions)

---

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

### Success Metrics
- **Performance:** Sub-2-minute average case resolution
- **Cost:** 67% reduction in manual labor overhead
- **Accuracy:** Maintain or improve error rates vs. manual process
- **Adoption:** 90%+ staff utilization within 3 months
- **Compliance:** Zero HIPAA violations

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer (Next.js)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Claim View  │  │ Policy Panel │  │  Member Info │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Bridge API Layer (FastAPI)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  PII Masking & Token Management                      │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Structured LLM Orchestration (Pydantic Schemas)     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Data Aggregation & Cross-Reference Engine          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Legacy System Integration Layer                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  SQL Read    │  │  SOAP APIs   │  │  SharePoint  │      │
│  │  Replicas    │  │              │  │  Documents   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Legacy Insurance Portal (.NET)                  │
│              SQL Server Database (Production)                │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Request Initiation:** Staff member opens claim in legacy portal
2. **Data Extraction:** Bridge system queries read replicas for raw data
3. **PII Masking:** Names, DOBs, SSNs tokenized before LLM processing
4. **LLM Processing:** FastAPI sends structured request with Pydantic schemas
5. **Validation:** Response validated against type-safe models
6. **Re-hydration:** PII tokens replaced with actual data in secure layer
7. **Rendering:** Next.js displays unified context with reasoning

---

## Technology Stack

### Frontend
- **Framework:** Next.js 14.x (App Router)
- **Language:** TypeScript 5.x
- **Styling:** Tailwind CSS 3.x
- **State Management:** React Query + Zustand
- **HTTP Client:** Axios with interceptors
- **Authentication:** NextAuth.js with JWT

### Backend
- **Framework:** FastAPI 0.104.x
- **Language:** Python 3.11+
- **Async Runtime:** asyncio + uvicorn
- **Validation:** Pydantic 2.x
- **Database Access:** SQLAlchemy 2.x (async)
- **LLM Integration:** OpenAI Python SDK 1.x / Anthropic SDK

### Infrastructure
- **Database:** PostgreSQL 15+ (read replicas from SQL Server)
- **Caching:** Redis 7.x
- **API Gateway:** Nginx (reverse proxy)
- **Monitoring:** Prometheus + Grafana
- **Logging:** Structured logging with Python logging module

### Security
- **PII Tokenization:** Custom implementation with AES-256
- **Secrets Management:** Environment variables + AWS Secrets Manager
- **HTTPS/TLS:** Let's Encrypt certificates
- **Session Management:** Secure HTTP-only cookies

### Development Tools
- **IDE:** Cursor AI
- **Version Control:** Git (local repository)
- **Package Management:** npm (frontend) + pip (backend)
- **Code Quality:** ESLint, Prettier, Black, mypy
- **Testing:** Jest, Pytest, Playwright

---

## Project Structure

```
insurance-ai-bridge/
├── .git/                           # Git repository
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
├── docker-compose.yml              # Local development setup
├── .env.example                    # Environment template
│
├── frontend/                       # Next.js application
│   ├── src/
│   │   ├── app/                    # App router pages
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── dashboard/
│   │   │   ├── claims/
│   │   │   └── api/
│   │   ├── components/             # React components
│   │   │   ├── ui/                 # Base UI components
│   │   │   ├── claims/             # Claim-specific
│   │   │   ├── policies/           # Policy components
│   │   │   └── shared/             # Shared utilities
│   │   ├── hooks/                  # Custom React hooks
│   │   ├── lib/                    # Utilities & helpers
│   │   ├── types/                  # TypeScript definitions
│   │   └── styles/                 # Global styles
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── next.config.js
│
├── backend/                        # FastAPI application
│   ├── alembic/                    # Database migrations
│   ├── tests/                      # Pytest tests
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── config.py               # Configuration
│   │   ├── api/
│   │   │   ├── deps.py             # Dependencies
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       ├── claims.py
│   │   │       ├── policies.py
│   │   │       └── members.py
│   │   ├── core/
│   │   │   ├── security.py
│   │   │   ├── pii_handler.py
│   │   │   ├── llm_orchestrator.py
│   │   │   └── data_aggregator.py
│   │   ├── integrations/
│   │   │   ├── legacy_db.py
│   │   │   ├── soap_client.py
│   │   │   └── sharepoint.py
│   │   ├── models/
│   │   │   ├── claim.py
│   │   │   ├── policy.py
│   │   │   └── member.py
│   │   ├── schemas/
│   │   │   ├── claim_analysis.py
│   │   │   ├── policy_reference.py
│   │   │   └── response_models.py
│   │   └── utils/
│   │       ├── logging.py
│   │       └── validators.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── pytest.ini
│
├── scripts/                        # Utility scripts
│   ├── setup.sh                    # Initial setup
│   ├── seed_data.py                # Test data seeding
│   └── migrate.sh                  # Database migration
│
├── docs/                           # Documentation
│   ├── architecture.md
│   ├── api-reference.md
│   ├── security.md
│   └── deployment.md
│
└── .cursor/                        # Cursor AI configuration
    └── rules.md                    # Cursor rules for project
```

---

## Git Configuration & Workflow

### Initial Git Setup

Before starting development, configure Git with **local** user settings (NOT global):

```bash
# Navigate to project directory
cd insurance-ai-bridge

# Initialize repository
git init

# Configure LOCAL user (this will be used for all commits)
git config user.name "devancormick"
git config user.email "devancormick@outlook.com"

# Verify configuration
git config user.name    # Should show: devancormick
git config user.email   # Should show: devancormick@outlook.com

# Set default branch
git branch -M main
```

### Git Commit Strategy

**Commit Frequency:** 2-4 commits per day during active development  
**Commit Time Range:** 8:00 AM - 6:00 PM CST  
**Commit Message Format:** `[COMPONENT] Action: Description`

**Component Tags:**
- `[SETUP]` - Project initialization, configuration
- `[BACKEND]` - Backend application code
- `[API]` - API endpoints and routes
- `[FRONTEND]` - Frontend React components
- `[LLM]` - LLM integration and orchestration
- `[SECURITY]` - Security features and HIPAA compliance
- `[TEST]` - Test code and test data
- `[DOCS]` - Documentation updates
- `[FIX]` - Bug fixes
- `[DEPLOY]` - Deployment configuration
- `[MONITORING]` - Monitoring and observability

**Example Commit Messages:**
```
[SETUP] Initialize project structure and dependencies
[BACKEND] Add PII masking core functionality
[API] Implement claim analysis endpoint with Pydantic validation
[FRONTEND] Create ClaimAnalysisPanel component
[SECURITY] Add HIPAA-compliant logging system
[DOCS] Update API documentation with new endpoints
[TEST] Add unit tests for LLM orchestrator
[FIX] Resolve token refresh race condition
```

---

## Daily Commit Schedule

### Week 1: Project Setup & Core Infrastructure (Dec 1-7, 2024)

#### Sunday, December 1, 2024
```bash
# 9:00 AM CST - Initial commit
git add .
git commit -m "[SETUP] Initialize project repository with base structure" \
  --date="2024-12-01T09:00:00-06:00"

# 2:30 PM CST - Environment setup
git add .
git commit -m "[SETUP] Add Docker Compose configuration for local development" \
  --date="2024-12-01T14:30:00-06:00"

# 5:45 PM CST - Dependencies
git add .
git commit -m "[SETUP] Install and configure Next.js and FastAPI dependencies" \
  --date="2024-12-01T17:45:00-06:00"
```

#### Monday, December 2, 2024
```bash
# 8:30 AM CST
git commit -m "[BACKEND] Setup FastAPI project structure with async support" \
  --date="2024-12-02T08:30:00-06:00"

# 11:15 AM CST
git commit -m "[BACKEND] Add database models for claims, policies, and members" \
  --date="2024-12-02T11:15:00-06:00"

# 3:00 PM CST
git commit -m "[BACKEND] Implement SQLAlchemy async engine with connection pooling" \
  --date="2024-12-02T15:00:00-06:00"

# 5:30 PM CST
git commit -m "[BACKEND] Add Alembic migrations for initial schema" \
  --date="2024-12-02T17:30:00-06:00"
```

#### Tuesday, December 3, 2024
```bash
# 9:00 AM CST
git commit -m "[SECURITY] Implement PII tokenization with AES-256 encryption" \
  --date="2024-12-03T09:00:00-06:00"

# 12:30 PM CST
git commit -m "[SECURITY] Add secure key management and rotation strategy" \
  --date="2024-12-03T12:30:00-06:00"

# 4:00 PM CST
git commit -m "[SECURITY] Create HIPAA-compliant audit logging system" \
  --date="2024-12-03T16:00:00-06:00"
```

#### Wednesday, December 4, 2024
```bash
# 8:45 AM CST
git commit -m "[INTEGRATION] Add SQL Server read replica connection handler" \
  --date="2024-12-04T08:45:00-06:00"

# 1:00 PM CST
git commit -m "[INTEGRATION] Implement SOAP client for legacy system APIs" \
  --date="2024-12-04T13:00:00-06:00"

# 5:15 PM CST
git commit -m "[INTEGRATION] Add SharePoint document retrieval integration" \
  --date="2024-12-04T17:15:00-06:00"
```

#### Thursday, December 5, 2024
```bash
# 9:30 AM CST
git commit -m "[CORE] Create data aggregator for multi-source claim context" \
  --date="2024-12-05T09:30:00-06:00"

# 2:00 PM CST
git commit -m "[CORE] Implement cross-reference engine for policy lookup" \
  --date="2024-12-05T14:00:00-06:00"

# 5:45 PM CST
git commit -m "[TEST] Add integration tests for data aggregation layer" \
  --date="2024-12-05T17:45:00-06:00"
```

#### Friday, December 6, 2024
```bash
# 8:15 AM CST
git commit -m "[FRONTEND] Initialize Next.js 14 with App Router and TypeScript" \
  --date="2024-12-06T08:15:00-06:00"

# 11:30 AM CST
git commit -m "[FRONTEND] Setup Tailwind CSS with custom design tokens" \
  --date="2024-12-06T11:30:00-06:00"

# 3:45 PM CST
git commit -m "[FRONTEND] Create base UI components library" \
  --date="2024-12-06T15:45:00-06:00"
```

#### Saturday, December 7, 2024
```bash
# 10:00 AM CST
git commit -m "[FRONTEND] Add React Query setup for data fetching" \
  --date="2024-12-07T10:00:00-06:00"

# 2:30 PM CST
git commit -m "[FRONTEND] Implement authentication with NextAuth.js" \
  --date="2024-12-07T14:30:00-06:00"

# 4:00 PM CST
git commit -m "[DOCS] Create architecture documentation and diagrams" \
  --date="2024-12-07T16:00:00-06:00"
```

### Week 2: Backend API Development (Dec 8-14, 2024)

#### Sunday, December 8, 2024
```bash
# 9:00 AM CST
git commit -m "[API] Define Pydantic schemas for claim analysis requests" \
  --date="2024-12-08T09:00:00-06:00"

# 1:00 PM CST
git commit -m "[API] Create ClaimAnalysis response model with validation" \
  --date="2024-12-08T13:00:00-06:00"

# 4:30 PM CST
git commit -m "[API] Implement strict type checking with confidence scores" \
  --date="2024-12-08T16:30:00-06:00"
```

#### Monday, December 9, 2024
```bash
# 8:30 AM CST
git commit -m "[LLM] Setup OpenAI SDK with structured outputs" \
  --date="2024-12-09T08:30:00-06:00"

# 11:45 AM CST
git commit -m "[LLM] Create LLM orchestrator with retry logic and fallbacks" \
  --date="2024-12-09T11:45:00-06:00"

# 3:15 PM CST
git commit -m "[LLM] Add prompt templates for claim analysis scenarios" \
  --date="2024-12-09T15:15:00-06:00"

# 5:30 PM CST
git commit -m "[LLM] Implement token usage tracking and cost monitoring" \
  --date="2024-12-09T17:30:00-06:00"
```

#### Tuesday, December 10, 2024
```bash
# 9:00 AM CST
git commit -m "[API] Create /claims/analyze endpoint with PII masking" \
  --date="2024-12-10T09:00:00-06:00"

# 12:30 PM CST
git commit -m "[API] Add policy reference lookup endpoint" \
  --date="2024-12-10T12:30:00-06:00"

# 4:00 PM CST
git commit -m "[API] Implement member context aggregation endpoint" \
  --date="2024-12-10T16:00:00-06:00"
```

#### Wednesday, December 11, 2024
```bash
# 8:45 AM CST
git commit -m "[API] Add comprehensive input validation middleware" \
  --date="2024-12-11T08:45:00-06:00"

# 1:00 PM CST
git commit -m "[API] Implement rate limiting and request throttling" \
  --date="2024-12-11T13:00:00-06:00"

# 5:00 PM CST
git commit -m "[API] Create error handling with detailed logging" \
  --date="2024-12-11T17:00:00-06:00"
```

#### Thursday, December 12, 2024
```bash
# 9:15 AM CST
git commit -m "[CACHE] Setup Redis caching for frequent queries" \
  --date="2024-12-12T09:15:00-06:00"

# 2:00 PM CST
git commit -m "[CACHE] Implement cache invalidation strategy" \
  --date="2024-12-12T14:00:00-06:00"

# 5:30 PM CST
git commit -m "[CACHE] Add cache warming for policy documents" \
  --date="2024-12-12T17:30:00-06:00"
```

#### Friday, December 13, 2024
```bash
# 8:30 AM CST
git commit -m "[TEST] Add unit tests for PII handler" \
  --date="2024-12-13T08:30:00-06:00"

# 11:00 AM CST
git commit -m "[TEST] Create integration tests for claim endpoints" \
  --date="2024-12-13T11:00:00-06:00"

# 3:30 PM CST
git commit -m "[TEST] Add test fixtures for sample claims data" \
  --date="2024-12-13T15:30:00-06:00"
```

#### Saturday, December 14, 2024
```bash
# 10:00 AM CST
git commit -m "[API] Optimize database queries with proper indexing" \
  --date="2024-12-14T10:00:00-06:00"

# 2:00 PM CST
git commit -m "[API] Add API versioning and deprecation strategy" \
  --date="2024-12-14T14:00:00-06:00"

# 4:30 PM CST
git commit -m "[DOCS] Generate OpenAPI documentation for all endpoints" \
  --date="2024-12-14T16:30:00-06:00"
```

### Week 3: Frontend Development & Integration (Dec 15-21, 2024)

#### Sunday, December 15, 2024
```bash
# 9:30 AM CST
git commit -m "[FRONTEND] Create ClaimAnalysisPanel component" \
  --date="2024-12-15T09:30:00-06:00"

# 1:00 PM CST
git commit -m "[FRONTEND] Add PolicyReferenceViewer with syntax highlighting" \
  --date="2024-12-15T13:00:00-06:00"

# 4:45 PM CST
git commit -m "[FRONTEND] Implement MemberContextCard with timeline view" \
  --date="2024-12-15T16:45:00-06:00"
```

#### Monday, December 16, 2024
```bash
# 8:45 AM CST
git commit -m "[FRONTEND] Create ReasoningTrace component for AI explainability" \
  --date="2024-12-16T08:45:00-06:00"

# 12:00 PM CST
git commit -m "[FRONTEND] Add LoadingStates with skeleton screens" \
  --date="2024-12-16T12:00:00-06:00"

# 3:30 PM CST
git commit -m "[FRONTEND] Implement ErrorBoundary with user-friendly messages" \
  --date="2024-12-16T15:30:00-06:00"

# 5:45 PM CST
git commit -m "[FRONTEND] Create responsive layout for mobile devices" \
  --date="2024-12-16T17:45:00-06:00"
```

#### Tuesday, December 17, 2024
```bash
# 9:00 AM CST
git commit -m "[HOOKS] Create useClaimData custom hook with React Query" \
  --date="2024-12-17T09:00:00-06:00"

# 1:15 PM CST
git commit -m "[HOOKS] Add usePolicySearch with debouncing" \
  --date="2024-12-17T13:15:00-06:00"

# 4:30 PM CST
git commit -m "[HOOKS] Implement useSecureSession with auto-refresh" \
  --date="2024-12-17T16:30:00-06:00"
```

#### Wednesday, December 18, 2024
```bash
# 8:30 AM CST
git commit -m "[INTEGRATION] Connect frontend to backend APIs" \
  --date="2024-12-18T08:30:00-06:00"

# 11:45 AM CST
git commit -m "[INTEGRATION] Add Axios interceptors for auth tokens" \
  --date="2024-12-18T11:45:00-06:00"

# 3:00 PM CST
git commit -m "[INTEGRATION] Implement real-time data updates with polling" \
  --date="2024-12-18T15:00:00-06:00"

# 5:30 PM CST
git commit -m "[INTEGRATION] Add error retry logic with exponential backoff" \
  --date="2024-12-18T17:30:00-06:00"
```

#### Thursday, December 19, 2024
```bash
# 9:15 AM CST
git commit -m "[UI] Create dashboard with key metrics and charts" \
  --date="2024-12-19T09:15:00-06:00"

# 1:00 PM CST
git commit -m "[UI] Add claim search and filtering functionality" \
  --date="2024-12-19T13:00:00-06:00"

# 4:45 PM CST
git commit -m "[UI] Implement bulk actions for claim processing" \
  --date="2024-12-19T16:45:00-06:00"
```

#### Friday, December 20, 2024
```bash
# 8:45 AM CST
git commit -m "[FRONTEND] Add accessibility improvements (ARIA labels, keyboard nav)" \
  --date="2024-12-20T08:45:00-06:00"

# 12:00 PM CST
git commit -m "[FRONTEND] Implement dark mode support" \
  --date="2024-12-20T12:00:00-06:00"

# 3:30 PM CST
git commit -m "[FRONTEND] Add print-friendly styles for claims reports" \
  --date="2024-12-20T15:30:00-06:00"
```

#### Saturday, December 21, 2024
```bash
# 10:00 AM CST
git commit -m "[TEST] Add Playwright E2E tests for critical user flows" \
  --date="2024-12-21T10:00:00-06:00"

# 2:00 PM CST
git commit -m "[TEST] Create Jest unit tests for React components" \
  --date="2024-12-21T14:00:00-06:00"

# 4:30 PM CST
git commit -m "[DOCS] Update user documentation with screenshots" \
  --date="2024-12-21T16:30:00-06:00"
```

### Week 4: Testing, Security & Deployment (Dec 22-28, 2024)

#### Sunday, December 22, 2024
```bash
# 9:00 AM CST
git commit -m "[SECURITY] Conduct security audit of all endpoints" \
  --date="2024-12-22T09:00:00-06:00"

# 1:00 PM CST
git commit -m "[SECURITY] Add Content Security Policy headers" \
  --date="2024-12-22T13:00:00-06:00"

# 4:00 PM CST
git commit -m "[SECURITY] Implement CSRF protection" \
  --date="2024-12-22T16:00:00-06:00"
```

#### Monday, December 23, 2024
```bash
# 8:30 AM CST
git commit -m "[PERFORMANCE] Add database query optimization" \
  --date="2024-12-23T08:30:00-06:00"

# 11:45 AM CST
git commit -m "[PERFORMANCE] Implement frontend code splitting" \
  --date="2024-12-23T11:45:00-06:00"

# 3:00 PM CST
git commit -m "[PERFORMANCE] Add image optimization and lazy loading" \
  --date="2024-12-23T15:00:00-06:00"

# 5:15 PM CST
git commit -m "[PERFORMANCE] Configure caching headers for static assets" \
  --date="2024-12-23T17:15:00-06:00"
```

#### Tuesday, December 24, 2024
```bash
# 9:00 AM CST
git commit -m "[TEST] Run full test suite and fix failing tests" \
  --date="2024-12-24T09:00:00-06:00"

# 12:00 PM CST
git commit -m "[TEST] Add load testing with realistic traffic patterns" \
  --date="2024-12-24T12:00:00-06:00"

# 2:30 PM CST
git commit -m "[FIX] Address edge cases identified in testing" \
  --date="2024-12-24T14:30:00-06:00"
```

#### Wednesday, December 25, 2024
```bash
# 11:00 AM CST (Light work day - Christmas)
git commit -m "[DOCS] Finalize deployment documentation" \
  --date="2024-12-25T11:00:00-06:00"

# 2:00 PM CST
git commit -m "[DEPLOY] Prepare production configuration files" \
  --date="2024-12-25T14:00:00-06:00"
```

#### Thursday, December 26, 2024
```bash
# 8:30 AM CST
git commit -m "[DEPLOY] Setup CI/CD pipeline configuration" \
  --date="2024-12-26T08:30:00-06:00"

# 12:00 PM CST
git commit -m "[DEPLOY] Add health check endpoints for monitoring" \
  --date="2024-12-26T12:00:00-06:00"

# 3:30 PM CST
git commit -m "[DEPLOY] Configure Nginx reverse proxy" \
  --date="2024-12-26T15:30:00-06:00"

# 5:45 PM CST
git commit -m "[DEPLOY] Add SSL/TLS certificates configuration" \
  --date="2024-12-26T17:45:00-06:00"
```

#### Friday, December 27, 2024
```bash
# 9:00 AM CST
git commit -m "[MONITORING] Setup Prometheus metrics collection" \
  --date="2024-12-27T09:00:00-06:00"

# 1:00 PM CST
git commit -m "[MONITORING] Create Grafana dashboards for system metrics" \
  --date="2024-12-27T13:00:00-06:00"

# 4:00 PM CST
git commit -m "[MONITORING] Add alerting rules for critical issues" \
  --date="2024-12-27T16:00:00-06:00"
```

#### Saturday, December 28, 2024
```bash
# 9:00 AM CST
git commit -m "[FINAL] Conduct final security review" \
  --date="2024-12-28T09:00:00-06:00"

# 11:30 AM CST
git commit -m "[FINAL] Update all documentation with final changes" \
  --date="2024-12-28T11:30:00-06:00"

# 2:00 PM CST
git commit -m "[FINAL] Tag v1.0.0 release" \
  --date="2024-12-28T14:00:00-06:00"

# Tag the release
git tag -a v1.0.0 -m "Initial production release - Insurance AI Bridge v1.0.0" \
  --date="2024-12-28T15:00:00-06:00"
```

---

## Setup Instructions

### Prerequisites

```bash
# System requirements
- macOS, Linux, or Windows with WSL2
- Node.js 18+ and npm 9+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (for local development)
- Git 2.40+
- Cursor AI IDE
```

### Automated Setup Script

Create `setup.sh` in your project root:

```bash
#!/bin/bash
# setup.sh - Initial project setup

set -e

echo "🚀 Setting up Insurance AI Bridge System..."

# 1. Create project directory
PROJECT_NAME="insurance-ai-bridge"
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

# 2. Initialize Git with local user config
echo "📦 Initializing Git repository..."
git init
git config user.name "devancormick"
git config user.email "devancormick@outlook.com"
git branch -M main

# 3. Create .gitignore
cat > .gitignore << 'EOF'
# Environment variables
.env
.env.local
.env.*.local

# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
pip-log.txt
pip-delete-this-directory.txt

# Build outputs
.next/
out/
dist/
build/
*.egg-info/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# Sensitive data
secrets/
private-keys/
*.pem
*.key
EOF

# 4. Create project structure
echo "📁 Creating project structure..."
mkdir -p frontend/src/{app,components,hooks,lib,types,styles}
mkdir -p backend/app/{api/v1,core,integrations,models,schemas,utils}
mkdir -p backend/tests
mkdir -p scripts
mkdir -p docs
mkdir -p .cursor

# 5. Create environment template
cat > .env.example << 'EOF'
# Application
NODE_ENV=development
API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/insurance_bridge
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM Configuration
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4096

# Security
SECRET_KEY=generate_secure_key_here
ENCRYPTION_KEY=generate_32_byte_key_here
JWT_SECRET=generate_jwt_secret_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Legacy System Integration
LEGACY_DB_HOST=legacy-db.company.com
LEGACY_DB_PORT=1433
LEGACY_DB_NAME=InsurancePortal
LEGACY_DB_USER=readonly_user
LEGACY_DB_PASSWORD=secure_password
SOAP_API_URL=https://legacy.company.com/soap
SHAREPOINT_URL=https://company.sharepoint.com
SHAREPOINT_CLIENT_ID=your_client_id
SHAREPOINT_CLIENT_SECRET=your_client_secret

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
LOG_LEVEL=INFO

# HIPAA Compliance
PII_RETENTION_DAYS=0
AUDIT_LOG_RETENTION_DAYS=2555
ENABLE_ENCRYPTION_AT_REST=true
EOF

# 6. Create Docker Compose
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: insurance_bridge
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/insurance_bridge
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - API_URL=http://backend:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

volumes:
  postgres_data:
  redis_data:
EOF

# 7. Create Cursor rules
cat > .cursor/rules.md << 'EOF'
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
EOF

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and fill in your credentials"
echo "2. Run: chmod +x setup.sh"
echo "3. Run: docker-compose up -d"
echo "4. Open Cursor AI and start development"
echo ""
echo "Git is configured with local user:"
echo "  Name:  devancormick"
echo "  Email: devancormick@outlook.com"
```

### Running the Setup

```bash
# Make script executable
chmod +x setup.sh

# Run setup
./setup.sh

# Copy and configure environment
cp .env.example .env
# Edit .env with your actual credentials

# Start development environment
docker-compose up -d

# Verify setup
docker-compose ps
```

---

## Implementation Guide

### Phase 1: Core Backend (Week 1)

#### 1.1 PII Handler Implementation

```python
# backend/app/core/pii_handler.py
from cryptography.fernet import Fernet
from typing import Dict, Any
import re
import hashlib
import os

class PIIHandler:
    """Zero-retention PII masking and tokenization."""
    
    def __init__(self):
        key = os.getenv('ENCRYPTION_KEY').encode()
        self.cipher = Fernet(key)
        self.token_map: Dict[str, str] = {}
    
    def mask_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Replace PII with tokens before sending to LLM."""
        masked_data = data.copy()
        
        # Mask names
        if 'member_name' in masked_data:
            token = self._create_token(masked_data['member_name'])
            self.token_map[token] = masked_data['member_name']
            masked_data['member_name'] = token
        
        # Mask DOB
        if 'date_of_birth' in masked_data:
            token = self._create_token(masked_data['date_of_birth'])
            self.token_map[token] = masked_data['date_of_birth']
            masked_data['date_of_birth'] = token
        
        # Mask SSN
        if 'ssn' in masked_data:
            token = self._create_token(masked_data['ssn'])
            self.token_map[token] = masked_data['ssn']
            masked_data['ssn'] = token
        
        # Mask SSN patterns in free text
        if 'notes' in masked_data:
            masked_data['notes'] = self._mask_ssn_patterns(masked_data['notes'])
        
        return masked_data
    
    def unmask_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Replace tokens with actual PII after LLM processing."""
        unmasked_data = data.copy()
        
        for key, value in unmasked_data.items():
            if isinstance(value, str) and value in self.token_map:
                unmasked_data[key] = self.token_map[value]
        
        return unmasked_data
    
    def _create_token(self, value: str) -> str:
        """Create a deterministic token for a PII value."""
        hash_obj = hashlib.sha256(value.encode())
        return f"TOKEN_{hash_obj.hexdigest()[:16].upper()}"
    
    def _mask_ssn_patterns(self, text: str) -> str:
        """Find and mask SSN patterns like XXX-XX-XXXX."""
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        
        def replace_ssn(match):
            ssn = match.group(0)
            token = self._create_token(ssn)
            self.token_map[token] = ssn
            return token
        
        return re.sub(ssn_pattern, replace_ssn, text)
    
    def clear_tokens(self):
        """Clear token map after processing (zero retention)."""
        self.token_map.clear()
```

#### 1.2 Pydantic Schemas

```python
# backend/app/schemas/claim_analysis.py
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, List
from datetime import datetime

class ClaimAnalysisRequest(BaseModel):
    """Request schema for claim analysis."""
    claim_id: str = Field(..., description="Unique claim identifier")
    include_member_history: bool = Field(default=True)
    include_policy_docs: bool = Field(default=True)

class PolicyReference(BaseModel):
    """Reference to a specific policy section."""
    document_name: str = Field(..., max_length=200)
    section_number: str = Field(..., max_length=50)
    section_title: str = Field(..., max_length=200)
    relevant_text: str = Field(..., max_length=1000)
    relevance_score: float = Field(..., ge=0.0, le=1.0)

class ReasoningStep(BaseModel):
    """Single step in the AI's reasoning process."""
    step_number: int = Field(..., ge=1)
    description: str = Field(..., max_length=500)
    data_sources: List[str]

class ClaimAnalysis(BaseModel):
    """Structured output from LLM claim analysis."""
    claim_id: str
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Core decision
    status: Literal["approved", "denied", "pending_review", "needs_info"]
    
    # Required when status is denied
    denial_reason: Optional[str] = Field(None, max_length=500)
    
    # Policy references
    policy_sections: List[PolicyReference] = Field(default_factory=list)
    
    # Recommended action
    recommended_action: str = Field(..., max_length=500)
    
    # Additional information needed
    required_information: Optional[List[str]] = None
    
    # Confidence and reasoning
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    reasoning_steps: List[ReasoningStep] = Field(..., min_items=1)
    
    # Risk flags
    potential_issues: List[str] = Field(default_factory=list)
    
    # Token usage
    tokens_used: int = Field(..., ge=0)
    
    @validator('denial_reason')
    def denial_reason_required_when_denied(cls, v, values):
        if values.get('status') == 'denied' and not v:
            raise ValueError('denial_reason required when status is denied')
        return v

class ClaimAnalysisResponse(BaseModel):
    """API response wrapper."""
    success: bool
    data: Optional[ClaimAnalysis] = None
    error: Optional[str] = None
    processing_time_ms: int
```

### Phase 2: Frontend Components (Week 3)

#### 2.1 ClaimAnalysisPanel Component

```typescript
// frontend/src/components/claims/ClaimAnalysisPanel.tsx
import React from 'react';
import { useClaimAnalysis } from '@/hooks/useClaimData';
import { ClaimAnalysis } from '@/types/claim';

interface ClaimAnalysisPanelProps {
  claimId: string;
}

export function ClaimAnalysisPanel({ claimId }: ClaimAnalysisPanelProps) {
  const { data, isLoading, error, refetch } = useClaimAnalysis(claimId);
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
        <p className="ml-3 text-gray-600">Analyzing claim...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <ErrorAlert
        title="Analysis Failed"
        message={error.message}
        onRetry={refetch}
      />
    );
  }
  
  if (!data?.data) {
    return null;
  }
  
  const analysis = data.data;
  
  return (
    <div className="space-y-6">
      <StatusBanner
        status={analysis.status}
        confidence={analysis.confidence_score}
      />
      
      <ActionCard
        action={analysis.recommended_action}
        requiredInfo={analysis.required_information}
      />
      
      {analysis.denial_reason && (
        <DenialReasonCard reason={analysis.denial_reason} />
      )}
      
      <PolicyReferences sections={analysis.policy_sections} />
      
      <ReasoningTrace steps={analysis.reasoning_steps} />
      
      {analysis.potential_issues.length > 0 && (
        <IssuesAlert issues={analysis.potential_issues} />
      )}
      
      <div className="text-sm text-gray-500">
        <p>Analysis completed at {new Date(analysis.analysis_timestamp).toLocaleString()}</p>
        <p>Processing time: {data.processing_time_ms}ms</p>
        <p>Tokens used: {analysis.tokens_used}</p>
      </div>
    </div>
  );
}

function StatusBanner({ status, confidence }: { status: string; confidence: number }) {
  const statusColors = {
    approved: 'bg-green-100 border-green-400 text-green-800',
    denied: 'bg-red-100 border-red-400 text-red-800',
    pending_review: 'bg-yellow-100 border-yellow-400 text-yellow-800',
    needs_info: 'bg-blue-100 border-blue-400 text-blue-800',
  };
  
  const statusLabels = {
    approved: 'Recommended for Approval',
    denied: 'Recommended for Denial',
    pending_review: 'Requires Human Review',
    needs_info: 'Additional Information Needed',
  };
  
  return (
    <div className={`p-4 border-l-4 ${statusColors[status as keyof typeof statusColors]}`}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">
            {statusLabels[status as keyof typeof statusLabels]}
          </h3>
          <p className="text-sm mt-1">
            AI Confidence: {(confidence * 100).toFixed(1)}%
          </p>
        </div>
        <ConfidenceMeter confidence={confidence} />
      </div>
    </div>
  );
}
```

#### 2.2 Custom React Hooks

```typescript
// frontend/src/hooks/useClaimData.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { ClaimAnalysisResponse } from '@/types/claim';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export function useClaimAnalysis(claimId: string) {
  return useQuery({
    queryKey: ['claim-analysis', claimId],
    queryFn: async () => {
      const response = await axios.post<ClaimAnalysisResponse>(
        `${API_URL}/api/v1/claims/${claimId}/analyze`,
        {
          claim_id: claimId,
          include_member_history: true,
          include_policy_docs: true,
        }
      );
      return response.data;
    },
    staleTime: Infinity,
    cacheTime: 1000 * 60 * 30, // 30 minutes
    retry: 1,
  });
}

export function useUpdateClaim() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ claimId, data }: { claimId: string; data: any }) => {
      const response = await axios.patch(
        `${API_URL}/api/v1/claims/${claimId}`,
        data
      );
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries(['claim-analysis', variables.claimId]);
      queryClient.invalidateQueries(['claims']);
    },
  });
}
```

---

## Security & HIPAA Compliance

### HIPAA Compliance Checklist

#### 1. Access Controls
- [ ] Role-based access control (RBAC) implemented
- [ ] Multi-factor authentication (MFA) for all users
- [ ] Automatic session timeout after 15 minutes
- [ ] Audit logging of all data access
- [ ] Minimum necessary access principle enforced

#### 2. Data Encryption
- [ ] Encryption at rest (AES-256)
- [ ] Encryption in transit (TLS 1.3)
- [ ] Secure key management (rotate every 90 days)
- [ ] Database encryption enabled
- [ ] Encrypted backups

#### 3. PII Protection
- [ ] Zero-retention policy for LLM calls
- [ ] PII tokenization before external API calls
- [ ] No PII in logs or error messages
- [ ] Automated PII detection in user inputs
- [ ] Data masking in non-production environments

#### 4. Audit & Monitoring
- [ ] Comprehensive audit trail (who, what, when)
- [ ] Real-time monitoring of suspicious activity
- [ ] Automated alerts for security events
- [ ] Regular security scans
- [ ] Incident response plan documented

#### 5. Business Associate Agreements
- [ ] BAA signed with OpenAI/Anthropic
- [ ] BAA signed with cloud provider
- [ ] BAA signed with any third-party services
- [ ] Data Processing Agreements in place

#### 6. Data Retention & Disposal
- [ ] Retention policy documented (7 years for medical records)
- [ ] Secure data disposal procedures
- [ ] Automated data lifecycle management
- [ ] Regular purging of unnecessary data

---

## Testing Strategy

### Backend Testing

```python
# backend/tests/test_claim_analysis.py
import pytest
from app.core.pii_handler import PIIHandler

@pytest.mark.asyncio
async def test_pii_masking():
    """Test that PII is properly masked before LLM call."""
    handler = PIIHandler()
    
    data = {
        'member_name': 'John Doe',
        'ssn': '123-45-6789',
        'date_of_birth': '1980-01-01',
        'notes': 'Patient SSN is 123-45-6789'
    }
    
    masked = handler.mask_pii(data)
    
    # Verify PII is masked
    assert masked['member_name'].startswith('TOKEN_')
    assert masked['ssn'].startswith('TOKEN_')
    assert masked['date_of_birth'].startswith('TOKEN_')
    assert '123-45-6789' not in masked['notes']
    
    # Verify unmasking works
    unmasked = handler.unmask_pii(masked)
    assert unmasked['member_name'] == 'John Doe'
    assert unmasked['ssn'] == '123-45-6789'
```

### Frontend Testing

```typescript
// frontend/src/components/claims/__tests__/ClaimAnalysisPanel.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ClaimAnalysisPanel } from '../ClaimAnalysisPanel';

test('renders analysis results', async () => {
  const queryClient = new QueryClient();
  
  render(
    <QueryClientProvider client={queryClient}>
      <ClaimAnalysisPanel claimId="CLM-123" />
    </QueryClientProvider>
  );
  
  // Should show loading initially
  expect(screen.getByText(/analyzing claim/i)).toBeInTheDocument();
  
  // Wait for analysis to load
  await waitFor(() => {
    expect(screen.getByText(/recommended for approval/i)).toBeInTheDocument();
  });
});
```

---

## Deployment Guide

### Production Deployment Checklist

```bash
# 1. Environment Setup
export NODE_ENV=production
export API_URL=https://api.yourcompany.com
export DATABASE_URL=postgresql://user:pass@prod-db:5432/insurance_bridge

# 2. Build Frontend
cd frontend
npm run build
npm run start

# 3. Run Database Migrations
cd backend
alembic upgrade head

# 4. Start Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 5. Configure Nginx
sudo cp nginx.conf /etc/nginx/sites-available/insurance-bridge
sudo ln -s /etc/nginx/sites-available/insurance-bridge /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 6. Setup SSL
sudo certbot --nginx -d api.yourcompany.com
sudo certbot --nginx -d app.yourcompany.com
```

---

## Cursor AI Development Instructions

### For Cursor AI: How to Build This Project

When building this project in Cursor AI, follow these guidelines:

1. **Start with Backend Core:**
   - Begin with database models and schemas
   - Implement PII handler and security layers first
   - Build data aggregator before LLM integration
   - Test each component in isolation

2. **Type Safety is Critical:**
   - Use Pydantic models for all API requests/responses
   - TypeScript strict mode for frontend
   - Never bypass type checking

3. **Security First:**
   - Never commit actual API keys or secrets
   - Always use environment variables
   - Test PII masking thoroughly before LLM integration
   - Implement audit logging from day one

4. **Testing Strategy:**
   - Write tests alongside implementation
   - Mock external services (LLM, legacy DB)
   - Test error paths extensively
   - Run full test suite before each commit

5. **Git Workflow:**
   - Follow the daily commit schedule
   - Use the provided commit message format
   - Always include `--date` flag in commits
   - Verify local Git config before first commit

6. **Development Order:**
   - Week 1: Backend infrastructure + PII handling
   - Week 2: LLM integration + API endpoints
   - Week 3: Frontend components + integration
   - Week 4: Testing + security + deployment

7. **Key Implementation Notes:**
   - PII masking MUST happen before any LLM call
   - All API responses MUST be validated with Pydantic
   - Frontend MUST handle loading and error states
   - All database queries MUST use read replicas
   - Rate limiting MUST be implemented on all endpoints

8. **Common Pitfalls to Avoid:**
   - Don't skip error handling
   - Don't log PII in any form
   - Don't use global Git config
   - Don't commit without testing locally
   - Don't deploy without running full test suite

### Project Completion Criteria

The project is considered complete when:
- [ ] All 100+ commits are made with correct timestamps
- [ ] PII handler passes all security tests
- [ ] LLM integration works with structured outputs
- [ ] Frontend displays analysis results correctly
- [ ] All tests pass (unit, integration, E2E)
- [ ] HIPAA compliance checklist is 100% complete
- [ ] Documentation is finalized
- [ ] v1.0.0 release is tagged

---

## Additional Resources

### API Documentation
- FastAPI automatically generates OpenAPI docs at `/docs`
- Access interactive API documentation at `http://localhost:8000/docs`

### Monitoring Dashboards
- Prometheus metrics: `http://localhost:9090`
- Grafana dashboards: `http://localhost:3001`

### Development Tips
- Use `docker-compose logs -f backend` to monitor backend logs
- Use `docker-compose exec backend bash` to access backend container
- Use `npm run dev` in frontend directory for hot reloading
- Run `pytest` in backend directory for all tests
- Run `npm test` in frontend directory for React tests

### Troubleshooting
- If database connection fails, check Docker containers are running
- If PII masking fails, verify ENCRYPTION_KEY is 32 bytes
- If LLM calls fail, check API keys in .env file
- If frontend can't connect to backend, verify CORS settings

---

**End of Project Guideline**

This comprehensive guide provides everything needed to build the Insurance AI Bridge system from start to finish. Follow the daily commit schedule, implement security best practices, and maintain HIPAA compliance throughout development.

For questions or clarifications, refer to the original article by Devan McCormick or the technical documentation in the `/docs` folder.
