# Schema & Compliance Verification Tasks

## 1. Pydantic Model Strictness
- [x] Implement `UserRegistrationResponse` with:
    - [x] `id`: Integer (Primary Key).
    - [x] `email`: EmailStr (RFC-compliant).
    - [x] `created_at`: datetime (ISO 8601 timezone-aware).
- [x] Implement `TokenExchangeResponse` with:
    - [x] `access_token`: String (JWT).
    - [x] `refresh_token`: String (JWT).
    - [x] `token_type`: Constant "bearer".
- [x] Implement `StandardActionResponse` with `detail` string.

## 2. Cryptographic Constraints
- [x] Verify `HS256` signing algorithm for all tokens.
- [x] Ensure **Access Token Secret** != **Refresh Token Secret**.
- [x] Implement `jti` (JWT ID) claims in tokens for granular blacklisting (Using full token as identifier).

## 3. Operational Requirements
- [x] **No Plaintext Passwords**: Verify bcrypt hashing in the registration and login flow.
- [x] **Zero-Trust Logic**: Ensure the system blocks requests *before* reaching any business logic if the token is blacklisted.
- [x] **401 Unauthorized**: Explicitly return HTTP 401 for all failed security validations.

## 4. Documentation Compliance
- [x] Configure FastAPI `Swagger UI` to display exact schema structures defined in Spec v1.4.
- [x] Ensure all error responses use the `StandardActionResponse` where applicable.
