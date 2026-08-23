# AI TradeQ — Authentication & Identity API Specification

**Document Version:** 1.0  
**Status:** Approved  
**Module:** Authentication & Identity API (Task #002)  
**Classification:** API Specification  

---

## Base Path
All authentication endpoints are prefixed with `/api/v1/auth`.  
All user profile endpoints are prefixed with `/api/v1/users`.

---

## Endpoints

### 1. Register User
- **Endpoint**: `POST /api/v1/auth/register`
- **Rate Limit**: 10 requests / minute
- **Request Body**:
  ```json
  {
    "email": "analyst@firm.com",
    "password": "SecurePassword123!",
    "first_name": "Jane",
    "last_name": "Doe"
  }
  ```
- **Responses**:
  - `201 Created`:
    ```json
    {
      "access_token": "eyJhbGciOi...",
      "refresh_token": "dGhpcy1pcy1hLXJlZnJlc2gtdG9rZW4...",
      "token_type": "bearer",
      "expires_in": 900
    }
    ```
  - `400 Bad Request`: Password fails policy.
  - `409 Conflict`: Email already registered.

---

### 2. Login User
- **Endpoint**: `POST /api/v1/auth/login`
- **Rate Limit**: 10 requests / minute
- **Request Body**:
  ```json
  {
    "email": "analyst@firm.com",
    "password": "SecurePassword123!"
  }
  ```
- **Responses**:
  - `200 OK`: Returns token pair (`access_token`, `refresh_token`, `expires_in`).
  - `401 Unauthorized`: `"Invalid email or password."`
  - `403 Forbidden`: Account locked or deactivated.

---

### 3. Refresh Access Token
- **Endpoint**: `POST /api/v1/auth/refresh`
- **Rate Limit**: 20 requests / minute
- **Request Body**:
  ```json
  {
    "refresh_token": "dGhpcy1pcy1hLXJlZnJlc2gtdG9rZW4..."
  }
  ```
- **Responses**:
  - `200 OK`: Returns new rotated token pair.
  - `401 Unauthorized`: Invalid, expired, or reused token.

---

### 4. Logout Session
- **Endpoint**: `POST /api/v1/auth/logout`
- **Request Body**:
  ```json
  {
    "refresh_token": "dGhpcy1pcy1hLXJlZnJlc2gtdG9rZW4..."
  }
  ```
- **Responses**:
  - `200 OK`: `{"message": "Successfully logged out session.", "status": "success"}`

---

### 5. Logout All Sessions
- **Endpoint**: `POST /api/v1/auth/logout-all`
- **Headers**: `Authorization: Bearer <access_token>`
- **Responses**:
  - `200 OK`: `{"message": "Successfully logged out 3 active session(s).", "status": "success"}`
  - `401 Unauthorized`: Invalid / expired token.

---

### 6. Get Current User Identity
- **Endpoint**: `GET /api/v1/auth/me`
- **Headers**: `Authorization: Bearer <access_token>`
- **Responses**:
  - `200 OK`:
    ```json
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "email": "analyst@firm.com",
      "first_name": "Jane",
      "last_name": "Doe",
      "full_name": "Jane Doe",
      "is_active": true,
      "is_verified": false,
      "is_locked": false,
      "roles": ["USER", "ANALYST"],
      "permissions": ["reports:read", "models:execute"],
      "created_at": "2026-08-23T22:00:00Z",
      "updated_at": "2026-08-23T22:00:00Z",
      "last_login_at": "2026-08-23T22:15:00Z"
    }
    ```

---

### 7. Change Password
- **Endpoint**: `POST /api/v1/auth/change-password`
- **Headers**: `Authorization: Bearer <access_token>`
- **Rate Limit**: 5 requests / minute
- **Request Body**:
  ```json
  {
    "current_password": "SecurePassword123!",
    "new_password": "BrandNewSecurePassword123!"
  }
  ```
- **Responses**:
  - `200 OK`: `{"message": "Password changed successfully. All active sessions have been invalidated.", "status": "success"}`
  - `400 Bad Request`: Incorrect current password or weak new password.

---

### 8. Update User Profile
- **Endpoint**: `PATCH /api/v1/users/me`
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "first_name": "Jane",
    "last_name": "Smith"
  }
  ```
- **Responses**:
  - `200 OK`: Returns updated `UserResponse`.
