# JWT Authentication Implementation

This document describes the JWT authentication implementation for the Smart Contracts Escrow Platform.

## Overview

The platform now uses JWT (JSON Web Token) authentication via `djangorestframework-simplejwt` instead of Django's session-based authentication. This provides a stateless, scalable authentication mechanism suitable for API-driven applications.

## Endpoints

### 1. User Registration
**Endpoint:** `POST /api/users/auth/register/`

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "password_confirm": "string",
  "first_name": "string",
  "last_name": "string"
}
```

**Response (201):**
```json
{
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "is_seller": false
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "refresh": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

**Features:**
- Validates password strength using Django's password validators
- Checks that password and password_confirm match
- Automatically creates a wallet for the new user
- Returns both access and refresh tokens

### 2. User Login
**Endpoint:** `POST /api/users/auth/login/`

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (401):**
```json
{
  "detail": "Invalid credentials"
}
```

### 3. Get Current User
**Endpoint:** `GET /api/users/auth/user/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "is_seller": false
}
```

**Response (401):** Unauthorized if no valid token provided

### 4. Refresh Access Token
**Endpoint:** `POST /api/users/auth/token/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Features:**
- Refresh token rotation enabled - returns new refresh token
- Old refresh token is blacklisted after use
- Refresh tokens expire after 7 days

## Token Configuration

The JWT tokens are configured with the following settings (in `settings.py`):

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),      # Access token expires after 1 hour
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),      # Refresh token expires after 7 days
    'ROTATE_REFRESH_TOKENS': True,                    # New refresh token on each refresh
    'BLACKLIST_AFTER_ROTATION': True,                 # Blacklist old refresh token
    'UPDATE_LAST_LOGIN': True,                        # Update last_login on token creation
    'ALGORITHM': 'HS256',                             # HMAC SHA-256 algorithm
    'SIGNING_KEY': SECRET_KEY,                        # Use Django SECRET_KEY
    'AUTH_HEADER_TYPES': ('Bearer',),                 # Authorization: Bearer <token>
}
```

## Frontend Integration

The frontend API client (`frontend/src/lib/api.ts`) is already configured to use JWT authentication:

1. Stores access token in localStorage
2. Automatically includes `Authorization: Bearer <token>` header in all requests
3. Handles token refresh when access token expires
4. All API endpoints are protected by JWT authentication by default

## Security Features

1. **Password Security**
   - Django password validators ensure strong passwords
   - Passwords are write-only and never returned in responses
   - Passwords are securely hashed using Django's password hasher

2. **Token Security**
   - Tokens are signed using HS256 algorithm
   - Secret key is loaded from environment variable
   - Short-lived access tokens (1 hour)
   - Refresh token rotation with blacklisting

3. **Authentication**
   - Proper permission classes on all endpoints
   - REST Framework enforces authentication by default
   - Protected endpoints return 401 for unauthenticated requests

## Testing

A comprehensive test suite is included in `backend/users/test_auth.py`:

```bash
cd backend
python manage.py test users.test_auth
```

Tests cover:
- User registration (success and error cases)
- User login (success and invalid credentials)
- Getting current user (authenticated and unauthenticated)
- Token refresh
- is_seller property

All 9 tests pass successfully.

## Usage Example

### Python/Django Test Client
```python
from django.test import Client
import json

client = Client()

# Register
response = client.post('/api/users/auth/register/', 
    data=json.dumps({
        'username': 'user',
        'email': 'user@example.com',
        'password': 'SecurePass123!',
        'password_confirm': 'SecurePass123!',
        'first_name': 'Test',
        'last_name': 'User'
    }),
    content_type='application/json')
tokens = response.json()['tokens']

# Use access token
response = client.get('/api/users/auth/user/',
    HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
```

### JavaScript/Fetch
```javascript
// Register
const response = await fetch('http://localhost:8000/api/users/auth/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'user',
    email: 'user@example.com',
    password: 'SecurePass123!',
    password_confirm: 'SecurePass123!',
    first_name: 'Test',
    last_name: 'User'
  })
});
const { tokens } = await response.json();

// Use access token
const userResponse = await fetch('http://localhost:8000/api/users/auth/user/', {
  headers: { 'Authorization': `Bearer ${tokens.access}` }
});
```

## Migration from Session-Based Auth

This implementation replaces Django's session-based authentication with JWT tokens:

- **Before:** Sessions stored in database, cookies used for authentication
- **After:** Stateless JWT tokens, no server-side session storage required
- **Benefits:** 
  - Better scalability (stateless)
  - Works across multiple domains
  - Mobile-friendly
  - No CSRF protection needed for API endpoints

## Dependencies

- `djangorestframework-simplejwt==5.5.1` - JWT authentication for DRF
- `PyJWT==2.10.1` - JWT encoding/decoding (dependency of simplejwt)

All dependencies have been checked for security vulnerabilities - none found.
