# AI TradeQ — Authentication & Identity Architecture

**Document Version:** 1.0  
**Status:** Approved  
**Module:** Authentication & Identity Management (Task #002)  
**Classification:** Engineering Architecture  

---

## 1. Overview

The AI TradeQ Authentication & Identity Management subsystem provides enterprise-grade identity lifecycle management, session orchestration, and role-based access control (RBAC).

### Key Architectural Pillars
- **Stateless Access Token Authentication**: Short-lived (15 minutes) signed JSON Web Tokens (JWT) containing standard claims (`sub`, `roles`, `permissions`, `jti`, `exp`, `iat`).
- **Stateful Refresh Token Rotation**: Long-lived (7 days) refresh tokens stored in hashed format with token family tracking, revocation mechanisms, and automatic reuse detection.
- **Role-Based Access Control (RBAC)**: Fine-grained permissions and hierarchical roles (`SUPER_ADMIN`, `ADMIN`, `ANALYST`, `USER`).
- **Account Lockout & Brute-Force Defense**: Configurable failure thresholds (5 attempts) triggering temporal lockouts (15 minutes).
- **Zero-Leakage Audit Logging**: Asynchronous security audit event recording with automatic redaction of credentials, tokens, and secrets.

---

## 2. Token Lifecycle & Family Rotation

```mermaid
sequenceDiagram
    autonumber
    actor Client as Frontend / Client
    participant Auth as Auth API
    participant DB as PostgreSQL DB
    participant Audit as Audit Logger

    Client->>Auth: POST /api/v1/auth/login {email, password}
    Auth->>DB: Query User & Verify Password Hash (Bcrypt)
    alt Credentials Valid & Not Locked
        Auth->>DB: Reset Failed Attempts, Record Login
        Auth->>DB: Insert Hashed Refresh Token (Family F1, Revoked=False)
        Auth->>Audit: Log LOGIN_SUCCESS (safe metadata)
        Auth-->>Client: 200 OK {access_token, refresh_token}
    else Invalid Password
        Auth->>DB: Increment Failed Attempts (Lock if >= 5)
        Auth->>Audit: Log LOGIN_FAILURE
        Auth-->>Client: 401 Unauthorized "Invalid email or password"
    end

    Note over Client,Auth: Access Token Expiry (15m) -> Token Refresh
    Client->>Auth: POST /api/v1/auth/refresh {refresh_token: R1}
    Auth->>DB: Query Refresh Token by Hash(R1)
    alt Token R1 is Valid & Not Revoked
        Auth->>DB: Mark R1 Revoked=True, Revoked_At=Now
        Auth->>DB: Insert New Hashed Refresh Token R2 (Same Family F1)
        Auth->>Audit: Log TOKEN_REFRESH
        Auth-->>Client: 200 OK {access_token, refresh_token: R2}
    else Token R1 was ALREADY Revoked (Reuse Attack)
        Auth->>DB: Revoke ALL Tokens in Family F1
        Auth->>Audit: Log TOKEN_REUSE_DETECTED (Security Alert)
        Auth-->>Client: 401 Unauthorized "Token reuse detected"
    end
```

---

## 3. Database Entity Schema

### User Entity (`users`)
- `id` (UUID, Primary Key)
- `email` (VARCHAR 255, Unique, Indexed)
- `password_hash` (VARCHAR 255, Bcrypt Hash)
- `first_name` (VARCHAR 100, Nullable)
- `last_name` (VARCHAR 100, Nullable)
- `is_active` (BOOLEAN, Default True)
- `is_verified` (BOOLEAN, Default False)
- `is_locked` (BOOLEAN, Default False)
- `failed_login_attempts` (INTEGER, Default 0)
- `locked_until` (TIMESTAMP WITH TIME ZONE, Nullable)
- `created_at` (TIMESTAMP WITH TIME ZONE, Server Default Now)
- `updated_at` (TIMESTAMP WITH TIME ZONE, Server Default Now)
- `last_login_at` (TIMESTAMP WITH TIME ZONE, Nullable)

### Refresh Token Entity (`refresh_tokens`)
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key -> `users.id` ON DELETE CASCADE)
- `token_hash` (VARCHAR 255, Unique, SHA-256 Hash of raw token)
- `family_id` (UUID, Indexed)
- `is_revoked` (BOOLEAN, Default False)
- `expires_at` (TIMESTAMP WITH TIME ZONE)
- `created_at` (TIMESTAMP WITH TIME ZONE)
- `revoked_at` (TIMESTAMP WITH TIME ZONE, Nullable)
- `user_agent` (VARCHAR 255, Nullable)
- `ip_address` (VARCHAR 45, Nullable)

### RBAC Entities (`roles`, `permissions`, `user_roles`, `role_permissions`)
- Many-to-many relationship connecting users to roles, and roles to granular permissions.

### Security Audit Log (`auth_audit_logs`)
- `id` (UUID, Primary Key)
- `user_id` (UUID, Nullable, Foreign Key -> `users.id` ON DELETE SET NULL)
- `event_type` (VARCHAR 50, Indexed)
- `status` (VARCHAR 20: SUCCESS, FAILURE, LOCKED, SECURITY_ALERT)
- `ip_address` (VARCHAR 45, Nullable)
- `user_agent` (VARCHAR 255, Nullable)
- `correlation_id` (VARCHAR 100, Nullable)
- `details` (TEXT / JSON, Strictly Redacted)
- `created_at` (TIMESTAMP WITH TIME ZONE)
