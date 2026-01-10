# Insurance AI Bridge System

**Project Name:** Insurance AI Bridge System  
**Status:** 🚀 Production Ready | 🔒 HIPAA Compliant | ⚡ High Performance

---

## 📊 Quick Preview

Before diving into the code, explore our **interactive visualizations** to see the system in action:

👉 **[Start with the Project Homepage →](index.html)** (Opens interactive navigation hub)

<details>
<summary><strong>📸 Visual Overview</strong> (Click to expand)</summary>

| Visualization | Description | Quick Link |
|--------------|-------------|-----------|
| 🏠 **Homepage** | Central hub with stats & navigation | [index.html](index.html) |
| 🏗️ **Architecture** | Complete system design | [system-architecture-viewer.html](visualizations/system-architecture-viewer.html) |
| 📊 **Dashboard** | Interactive claim processing | [ai_bridge_dashboard.html](visualizations/ai_bridge_dashboard.html) |
| ⚡ **Live System** | Real-time data streaming | [dashboard-live-system.html](visualizations/dashboard-live-system.html) |
| 🔍 **Claim Viewer** | Step-by-step AI analysis | [claim-analysis-viewer.html](visualizations/claim-analysis-viewer.html) |
| 🔒 **Security** | HIPAA compliance features | [security-compliance.html](visualizations/security-compliance.html) |
| 💰 **Cost Analysis** | ROI & savings breakdown | [cost-savings.html](visualizations/cost-savings.html) |

**💡 Tip:** Press `Ctrl+K V` in Cursor/VS Code to preview any HTML file side-by-side!

</details>

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

## 📊 Interactive Visualizations

> **See the project in action before running!** Interactive HTML visualizations showcase the system architecture, live processing, security features, and cost savings.

### 🖼️ Visual Preview Gallery

Click any visualization below to view it, or use the [Project Homepage](index.html) for navigation:

<details>
<summary><strong>🏠 Project Homepage</strong> - Central hub with navigation (Click to expand)</summary>

**File:** [`index.html`](index.html)

**Features:**
- ✨ Beautiful gradient homepage with key metrics
- 📊 Real-time stats: 89% faster processing, $28K monthly savings, 98.7% accuracy
- 🎯 Navigation cards to all 6 visualizations
- 🔑 Key features overview with icons
- 🛠️ Tech stack badges

**Visual Elements:**
- Dark theme with blue/purple gradients
- Interactive hover effects on navigation cards
- Responsive grid layout
- Quick links section for documentation

[▶️ Open index.html](index.html) | [📖 Viewing Guide](docs/project/VIEW-VISUALIZATIONS.md)

</details>

<details>
<summary><strong>🏗️ System Architecture Viewer</strong> - Complete technical architecture (Click to expand)</summary>

**File:** [`system-architecture-viewer.html`](visualizations/system-architecture-viewer.html)

**Features:**
- 🏛️ 4-layer architecture visualization (Frontend → API → Integration → Legacy)
- 📦 Component breakdown with tech tags
- 🔄 Data flow arrows between layers
- 🔒 Security features showcase
- ⚡ Performance metrics display
- ✨ Animated particle background

**Visual Elements:**
- GitHub-style dark theme
- Layer cards with hover effects
- Tech stack breakdown in organized grids
- Security compliance cards with icons
- Animated floating particles

[▶️ Open system-architecture-viewer.html](visualizations/system-architecture-viewer.html)

</details>

<details>
<summary><strong>📊 Interactive Dashboard</strong> - Claim processing workflow (Click to expand)</summary>

**File:** [`ai_bridge_dashboard.html`](visualizations/ai_bridge_dashboard.html)

**Features:**
- 🔄 Real-time architecture flow diagram (4-stage process)
- 📝 Interactive claim analysis interface with textarea input
- ⚙️ Animated process steps (5 stages with progress tracking)
- 📈 Live metrics cards (processing time, savings, claims processed, accuracy)
- 🎨 Status badges (approved/denied/pending)
- 🎭 Interactive animations on button click

**Visual Elements:**
- Dark slate theme (#0f172a)
- Blue/purple gradient accents
- Animated step progression
- Live loading spinners
- Interactive result cards

[▶️ Open ai_bridge_dashboard.html](visualizations/ai_bridge_dashboard.html)

</details>

<details>
<summary><strong>⚡ Live System Dashboard</strong> - Real-time data streaming (Click to expand)</summary>

**File:** [`dashboard-live-system.html`](visualizations/dashboard-live-system.html)

**Features:**
- 📊 Live stats bar with animated counters
- 🔄 System data flow visualization (5 steps)
- 💾 Live data streaming simulation (incoming raw data + AI output)
- 📋 Analysis results with confidence scores
- 📈 Cost comparison bar chart
- ✨ Animated grid background

**Visual Elements:**
- Cyberpunk theme with neon green/blue accents
- Real-time streaming text in terminal-style panels
- Animated bar charts showing cost savings
- Pulsing status indicators
- Live data lines with timestamps

[▶️ Open dashboard-live-system.html](visualizations/dashboard-live-system.html)

</details>

<details>
<summary><strong>🔍 Claim Analysis Viewer</strong> - Step-by-step AI analysis (Click to expand)</summary>

**File:** [`claim-analysis-viewer.html`](visualizations/claim-analysis-viewer.html)

**Features:**
- 📋 Claim details panel with metadata
- ⏱️ Processing timeline with 6 animated steps
- 🤖 AI analysis results with reasoning steps
- 📑 Policy reference cards with highlighted sections
- 🔒 PII protection demonstration table
- ✅ Action buttons (Approve/View Report)

**Visual Elements:**
- Clean light theme with blue accents
- Timeline with success markers
- Status banners (approved/denied/review) with gradients
- Policy cards with syntax highlighting
- Interactive hover effects

[▶️ Open claim-analysis-viewer.html](visualizations/claim-analysis-viewer.html)

</details>

<details>
<summary><strong>🔒 Security & Compliance</strong> - HIPAA compliance features (Click to expand)</summary>

**File:** [`security-compliance.html`](visualizations/security-compliance.html)

**Features:**
- ✅ 6 HIPAA compliance cards with checklists
- 🔄 PII protection flow (6-step process visualization)
- 📊 PII masking example table (before/after tokenization)
- 🛡️ Security features breakdown
- 🔐 Encryption details
- 📝 Audit logging information

**Visual Elements:**
- Security-themed dark green/blue palette
- Interactive compliance cards with hover effects
- Step-by-step PII flow with numbered badges
- Color-coded status badges (Masked/Secure)
- Code-styled token examples

[▶️ Open security-compliance.html](visualizations/security-compliance.html)

</details>

<details>
<summary><strong>💰 Cost Savings Analysis</strong> - ROI breakdown and savings (Click to expand)</summary>

**File:** [`cost-savings.html`](visualizations/cost-savings.html)

**Features:**
- 💵 Annual savings highlight ($336,000)
- 📊 Monthly cost comparison bar chart (Before: $40K → After: $12K)
- 📈 Key metrics grid (89% faster, $28K savings, 847 claims/day, 12.3% error reduction)
- 💼 ROI breakdown (6 metrics: time savings, cost, payback period, productivity, accuracy)
- 📋 Cost structure analysis (before/after breakdown)

**Visual Elements:**
- Clean white theme with green/blue gradients
- Animated bar charts with hover effects
- Large savings highlight banner
- ROI cards with visual hierarchy
- Side-by-side cost comparison

[▶️ Open cost-savings.html](visualizations/cost-savings.html)

</details>

---

### 🚀 Quick View Options

**Method 1: Built-in Preview (No Extension)**
- Open any `.html` file in Cursor/VS Code
- Press `Ctrl+K V` (Windows/Linux) or `Cmd+K V` (Mac)
- Preview opens side-by-side with auto-refresh!

**Method 2: Live Server Extension**
- Right-click `index.html` → "Open with Live Server"
- Opens in browser at `http://127.0.0.1:5500`

**Method 3: Simple Browser**
- Press `Ctrl+Shift+P` → "Simple Browser: Show"
- Enter file path to view in-editor

> 📖 **Detailed instructions:** See [VIEW-VISUALIZATIONS.md](docs/project/VIEW-VISUALIZATIONS.md) and [.vscode/HTML-PREVIEW-GUIDE.md](.vscode/HTML-PREVIEW-GUIDE.md)

---

## Documentation

### Interactive Visualizations
- [🏠 Project Homepage](index.html) - Central navigation hub
- [📊 Visualizations Guide](docs/project/VISUALIZATIONS.md) - Complete guide to all HTML visualizations
- [👁️ Quick Viewing Guide](docs/project/VIEW-VISUALIZATIONS.md) - How to view HTML files

### Technical Documentation
- [Architecture Documentation](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Security Guidelines](docs/security.md)
- [Deployment Guide](docs/deployment.md)
- [Git Workflow Guide](docs/git-workflow.md) - Complete Git workflow and branching strategy
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute to the project

## License

Proprietary - Internal Use Only