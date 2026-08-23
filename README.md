# AI TradeQ

## Vision
AI TradeQ is an enterprise-grade AI SaaS platform engineered to provide autonomous financial market analysis, intelligent quantitative trading strategy generation, real-time risk assessment, and automated portfolio optimization for institutional and retail traders.

## Folder Overview
```text
AI-TradeQ/
├── docs/            # Centralized platform documentation, PRDs, architecture, and ADRs
├── frontend/        # Web application user interface and frontend component architecture
├── backend/         # Core API services, domain business logic, and microservices
├── ai-services/     # Machine learning models, quantitative algorithms, and AI agent frameworks
├── infrastructure/  # Infrastructure as Code (IaC), cloud deployment manifests, and orchestration
├── scripts/         # Utility scripts, automated tooling, database migration scripts, and maintenance
└── .github/         # GitHub workflows, CI/CD pipeline definitions, and repository templates
```

## Technology Stack
- **Frontend**: Next.js 14+ (App Router) / React 18 / TypeScript / TailwindCSS / Radix UI / React Query
- **Backend**: Python 3.12+ (FastAPI) / SQLAlchemy 2.0 (Async) / Alembic / Pydantic v2
- **AI & MCP Foundation**: Model Context Protocol (MCP) Providers / Multi-Agent Frameworks
- **Database & Caching**: PostgreSQL 16+ / Redis 7+ / Qdrant (Vector DB)
- **Tooling & Runtimes**: Node.js 22 LTS / pnpm 9+ (Workspaces) / Docker & Docker Compose
- **Observability & Quality**: Ruff / Black / ESLint / Prettier / Pytest / OpenTelemetry

## Development Workflow
1. **Branching Strategy**: Follow GitFlow model (`main` for production, `develop` for integration, `feature/*` for new capabilities).
2. **Pull Requests**: All code changes require pull requests with code reviews, mandatory automated test checks, and architecture approval.
3. **Commit Standards**: Standard Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`).
4. **Local Development**: Utilize standard environment isolation per service directory (`frontend/`, `backend/`, `ai-services/`, `packages/`).

## Documentation Structure
All platform documentation is maintained under the `docs/` directory following a structured 21-tier numbering convention:
- `docs/01_Project_Charter/` - Strategic goals, constraints, and project governance
- `docs/02_Vision/` - Enterprise vision, target market, and strategic positioning
- `docs/03_PRD/` - Product Requirements Document (Functional and Non-Functional)
- `docs/04_SRS/` - Software Requirements Specification and interface requirements
- `docs/05_System_Architecture/` - High-level system architecture and micro-monolith structure
- `docs/06_AI_Agent_Architecture/` - AI agent workflows, memory systems, and prompt orchestration
- `docs/07_Database_Design/` - PostgreSQL data schemas, tables, indices, and caching models
- `docs/08_API_Specification/` - REST API endpoints, schemas, and error contract specifications
- `docs/09_MCP_Tool_Integration/` - Model Context Protocol tool contracts and provider registry
- `docs/10_Security_Architecture/` - Security policies, JWT auth, RBAC, and threat models
- `docs/11_UI_UX_Specification/` - Design system guidelines, layout specifications, and theme standards
- `docs/12_Testing_Strategy/` - Comprehensive test pyramid, unit, integration, and e2e testing
- `docs/13_Deployment_Architecture/` - Containerization, Kubernetes manifests, and cloud topology
- `docs/14_Development_Constitution/` - Core architectural rules, standards, and guidelines
- `docs/15_Product_Roadmap/` - Phased feature roadmap and enterprise release milestones
- `docs/16_Implementation_Plan/` - Engineering execution phases and work breakdown structure
- `docs/17_Backlog/` - Epics, user stories, and acceptance criteria
- `docs/18_Sprint_Planning/` - Sprint schedule, velocity planning, and task allocations
- `docs/19_Risk_Register/` - Technical, architectural, operational, and financial risks
- `docs/20_Glossary/` - Authoritative financial, trading, and engineering terminology
- `docs/21_Documentation_Index/` - Master documentation catalog and governance index
- `docs/ADR/` - Architecture Decision Records tracking key technological decisions
