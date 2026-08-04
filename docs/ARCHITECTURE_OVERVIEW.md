# Architecture Overview Guide

AI TradeQ follows an enterprise multi-tier architecture:
- **Presentation Layer**: Next.js App Router (TypeScript, Tailwind, shadcn/ui).
- **Application Layer**: FastAPI (Async Python, Pydantic, SQLAlchemy 2.0).
- **AI Tooling Layer**: Model Context Protocol (MCP) Ready Provider Abstraction.
- **Data Layer**: PostgreSQL (Relational/RBAC), Redis (Cache/Session).
- **Infrastructure**: Docker Compose, GitHub Actions CI/CD.
