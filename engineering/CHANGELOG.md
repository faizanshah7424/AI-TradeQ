# Engineering Changelog

## [0.2.0-auth] - 2026-08-23
### Added
- Authentication & Identity Management foundation (Task #002).
- UUID-based User, Role, Permission, UserRole, RolePermission, RefreshToken, and AuthAuditLog models.
- JWT access tokens (15-min) and stateful refresh token rotation (7-day) with token family reuse detection.
- Centralized RBAC authorization layer (`require_authenticated_user`, `require_role`, `require_permission`).
- Password policy validation and Bcrypt password hashing with constant-time verification.
- Configurable account lockout after 5 consecutive failed attempts (15-min lockout window).
- Sliding-window rate limiting dependency for sensitive auth endpoints.
- Auth API endpoints: `/register`, `/login`, `/refresh`, `/logout`, `/logout-all`, `/me`, `/change-password`.
- User profile endpoints: `GET /api/v1/users/me`, `PATCH /api/v1/users/me` with safe field validation.
- Audit logging service with automatic redaction safeguards.
- Alembic database migration `002_authentication_and_identity_tables.py` with initial role seeding.
- Comprehensive backend test suite across registration, login, lockout, tokens, authorization, password change, logout, audit logs, and profiles.
- Frontend auth foundation: API client with error handling, Zustand auth store with session hydration, interactive login and registration pages, and protected dashboard layout.
- Architecture and API specifications in `docs/10_Security_Architecture/` and `docs/08_API_Specification/`.
### Added
- Enterprise folder structure across frontend, backend, packages, engineering, docker, scripts, and docs.
- Next.js App Router setup with TypeScript, Tailwind CSS, TanStack Query, Zustand, Theme Provider, and Error Boundaries.
- FastAPI backend application factory with CORS, request logging, security middleware, and health endpoints.
- Database layer configured with PostgreSQL, SQLAlchemy 2.0, Alembic, and RBAC models (Users, Roles, Permissions).
- MCP Ready Abstraction Layer (Provider, Registry, Tool interfaces, Mock adapter).
- AI Foundation directory placeholders.
- Docker Compose orchestration with PostgreSQL 16, Redis 7, FastAPI, and Next.js.
- Complete GitHub governance templates, CI pipeline (GitHub Actions), and code standards (ESLint, Prettier, Ruff, Black, Pytest).
