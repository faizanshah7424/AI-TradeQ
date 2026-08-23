# AI TradeQ — Authentication Security Controls & Policies

**Document Version:** 1.0  
**Status:** Approved  
**Module:** Authentication Security Controls (Task #002)  
**Classification:** Security Governance  

---

## 1. Password Policy & Cryptography

1. **Hashing Standard**:
   - Primary algorithm: Bcrypt with automatic salt generation and work factor tuning via Passlib (`CryptContext(schemes=["bcrypt"], deprecated="auto")`).
   - Constant-time verification is enforced to mitigate side-channel timing attacks.
2. **Complexity Enforcement**:
   - Minimum length: 8 characters (`PASSWORD_MIN_LENGTH`).
   - Complexity requirements: At least 1 uppercase letter, 1 lowercase letter, 1 numeric digit, and 1 special character (`!@#$%^&*(),.?":{}|<>`).
3. **Storage & Logging Safeguards**:
   - Plaintext passwords are never persisted to disk, database, or cache.
   - Passwords and secrets are stripped and redacted (`[REDACTED]`) before any audit log writes.

---

## 2. Token Security & Session Invalidation

1. **Access Token Protections**:
   - Short lifespan: 15 minutes.
   - Strict cryptographic signing (`HS256` / `RS256` configurable).
   - Minimal claims payload: User ID (`sub`), role assignments (`roles`), permissions (`permissions`), unique token identifier (`jti`).
2. **Refresh Token Rotation & Storage**:
   - Refresh tokens are 256-bit cryptographically secure pseudorandom strings (`secrets.token_urlsafe(64)`).
   - Only SHA-256 hashes (`token_hash`) of refresh tokens are stored in the database.
   - Every refresh request invalidates the prior refresh token and issues a new token within the same token family (`family_id`).
3. **Reuse Detection (Replay Defense)**:
   - If a previously invalidated refresh token is presented, the system detects a session compromise attempt, revokes **all** active tokens in that token family, and records a `TOKEN_REUSE_DETECTED` security audit event.
4. **Session Invalidation**:
   - Password changes immediately revoke all active refresh tokens for the user account.
   - Explicit `POST /api/v1/auth/logout` revokes the specific session.
   - `POST /api/v1/auth/logout-all` revokes all active sessions across all devices.

---

## 3. Brute-Force & Abuse Mitigation

1. **Account Lockout**:
   - Threshold: 5 consecutive failed login attempts (`MAX_FAILED_LOGIN_ATTEMPTS`).
   - Lockout duration: 15 minutes (`LOCKOUT_DURATION_MINUTES`).
   - Counter resets to zero upon successful authentication.
2. **Generic Error Responses**:
   - Authentication failures return generic error messages (`"Invalid email or password."`) with uniform status codes (`401 Unauthorized`) to prevent user enumeration attacks.
3. **Rate Limiting**:
   - Sensitive endpoints (`/login`, `/register`, `/refresh`, `/change-password`) are protected by sliding-window rate limiters.
