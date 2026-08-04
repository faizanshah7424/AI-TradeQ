# AI TradeQ – Engineering Memory

## Architectural Overview
This document tracks system memory, active architectural context, core patterns, and operational state across engineering cycles.

## Current System Phase
- **Phase**: Bootstrap & Enterprise Foundation (Task #001)
- **Status**: Completed
- **Core Stack**: Next.js App Router (Frontend), FastAPI (Backend), PostgreSQL 16, Redis 7, Docker Compose, Alembic, SQLAlchemy.

## Critical Guidelines
- **No Crypto Business Logic**: Foundation only.
- **No AI Execution Logic**: Multi-provider and MCP registry abstraction layers only.
- **Security First**: RBAC entities, JWT primitives, CORS, Security Headers, and Healthcheck boundaries.
