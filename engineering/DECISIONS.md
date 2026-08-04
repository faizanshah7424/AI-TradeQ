# Architectural Decisions Log (Engineering)

## Decision Log

### ADR-001: Next.js App Router & FastAPI Micro-Monolith Architecture
- **Date**: 2026-07-30
- **Status**: Approved
- **Context**: Need high-performance, SEO-friendly SSR frontend combined with high-throughput async Python backend for AI agent processing.
- **Decision**: Adopt Next.js 14+ (App Router) for presentation and FastAPI for application/AI integration services.

### ADR-002: Model Context Protocol (MCP) Ready Abstraction
- **Date**: 2026-07-30
- **Status**: Approved
- **Context**: AI TradeQ requires extensible tool integration with third-party quantitative tools, market feeds, and news APIs.
- **Decision**: Implement abstract MCP provider, registry, and tool interfaces prior to concrete API bindings.
