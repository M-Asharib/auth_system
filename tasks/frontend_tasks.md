# Frontend / Client Validation Tasks

## Phase 1: Setup & Connection
- [x] Initialize a lightweight Vite + React/Vue client (Implemented as Premium SPA).
- [x] Setup `Axios` or `Fetch` interceptors for JWT handling.
- [x] Configure environment variables for the Backend API URL.

## Phase 2: Authentication UI
- [x] Build **Registration Form** with validation.
- [x] Build **Login Form** and state management (Store tokens in Secure Storage).
- [x] Implement a **Protected Dashboard** route.

## Phase 3: Token Lifecycle Logic
- [x] Implement **Auto-Refresh** logic (Implemented as Rotation Trigger).
- [x] Build **Logout Trigger** to call `/auth/logout` and clear local state.
- [x] Add visual indicators for "Access Token Status" vs "Refresh Token Status".

## Phase 4: Security Verification
- [ ] Create a "Malicious Request" button to test blacklisted token rejection.
- [ ] Verify `TokenExchangeResponse` parsing accuracy.
