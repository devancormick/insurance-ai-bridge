# System Architecture

## High-Level Architecture

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
```

## Data Flow

1. **Request Initiation:** Staff member opens claim in legacy portal
2. **Data Extraction:** Bridge system queries read replicas for raw data
3. **PII Masking:** Names, DOBs, SSNs tokenized before LLM processing
4. **LLM Processing:** FastAPI sends structured request with Pydantic schemas
5. **Validation:** Response validated against type-safe models
6. **Re-hydration:** PII tokens replaced with actual data in secure layer
7. **Rendering:** Next.js displays unified context with reasoning

## Component Details

### Frontend (Next.js)
- **App Router:** Modern Next.js routing
- **React Query:** Server state management
- **TypeScript:** Full type safety
- **Tailwind CSS:** Utility-first styling

### Backend (FastAPI)
- **Async/Await:** Non-blocking I/O operations
- **Pydantic:** Request/response validation
- **SQLAlchemy:** Async database access
- **LLM Integration:** OpenAI/Anthropic with structured outputs

### Security Layer
- **PII Handler:** Tokenization and masking
- **Audit Logging:** Comprehensive activity tracking
- **Encryption:** AES-256 for sensitive data
- **Access Control:** JWT-based authentication

