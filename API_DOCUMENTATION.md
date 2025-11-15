# Escrow Platform API Documentation

## Overview

This document provides comprehensive documentation for the Smart Contracts Escrow Platform API.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

All API endpoints require authentication. The API uses Django REST Framework's SessionAuthentication.

## API Endpoints

### Portal Endpoints

Portal endpoints provide specialized views for buyers and sellers to manage their transactions.

#### Buyer Dashboard

Get all transactions where the authenticated user is the buyer.

**Endpoint:** `GET /api/portal/my-transactions/`

**Authorization:** Requires authentication

**Response:** (200 OK)
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Website Development Project",
      "total_value": "800.00",
      "buyer": 1,
      "buyer_name": "buyer_user",
      "seller": 2,
      "seller_name": "seller_user",
      "status": "IN_ESCROW",
      "created_at": "2025-11-13T15:00:00Z",
      "milestones": [
        {
          "id": 1,
          "title": "Design Phase",
          "description": "Create initial designs",
          "value": "300.00",
          "status": "PENDING",
          "submission_details": ""
        }
      ]
    }
  ]
}
```

**Features:**
- Returns only transactions where the authenticated user is the buyer
- Includes milestone details for each transaction
- Shows buyer and seller information
- Ordered by most recent first
- Supports pagination

#### Seller Dashboard

Get all transactions where the authenticated user is the seller.

**Endpoint:** `GET /api/portal/seller/`

**Authorization:** Requires authentication

**Response:** (200 OK)
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Website Development Project",
      "total_value": "800.00",
      "buyer": 1,
      "buyer_name": "buyer_user",
      "seller": 2,
      "seller_name": "seller_user",
      "status": "IN_ESCROW",
      "created_at": "2025-11-13T15:00:00Z",
      "milestones": [
        {
          "id": 1,
          "title": "Design Phase",
          "description": "Create initial designs",
          "value": "300.00",
          "status": "PENDING",
          "submission_details": ""
        }
      ]
    }
  ]
}
```

**Features:**
- Returns only transactions where the authenticated user is the seller
- Includes milestone details for each transaction
- Shows buyer and seller information
- Ordered by most recent first
- Supports pagination

**Retrieve Individual Transaction:**

Sellers can retrieve details of a specific transaction:

**Endpoint:** `GET /api/portal/seller/{id}/`

**Response:** (200 OK) - Returns single transaction object

### Transactions

#### Create Transaction

Create a new escrow transaction with milestones.

**Endpoint:** `POST /api/transactions/`

**Request Body:**
```json
{
  "title": "Website Development Project",
  "seller": 2,
  "milestones": [
    {
      "title": "Design Phase",
      "description": "Create initial designs and mockups",
      "value": "300.00"
    },
    {
      "title": "Development Phase",
      "description": "Build the application",
      "value": "500.00"
    }
  ]
}
```

**Response:** (201 Created)
```json
{
  "id": 1,
  "title": "Website Development Project",
  "total_value": "800.00",
  "buyer": {
    "id": 1,
    "username": "buyer_user",
    "email": "buyer@example.com"
  },
  "seller": {
    "id": 2,
    "username": "seller_user",
    "email": "seller@example.com"
  },
  "status": "PENDING_FUNDING",
  "created_at": "2025-11-13T15:00:00Z",
  "milestones": [
    {
      "id": 1,
      "title": "Design Phase",
      "description": "Create initial designs and mockups",
      "value": "300.00",
      "status": "PENDING",
      "submission_details": ""
    },
    {
      "id": 2,
      "title": "Development Phase",
      "description": "Build the application",
      "value": "500.00",
      "status": "PENDING",
      "submission_details": ""
    }
  ]
}
```

#### List Transactions

Get all transactions where the authenticated user is buyer or seller.

**Endpoint:** `GET /api/transactions/`

**Response:** (200 OK)
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Website Development Project",
      "total_value": "800.00",
      "buyer": {...},
      "seller": {...},
      "status": "IN_ESCROW",
      "created_at": "2025-11-13T15:00:00Z",
      "milestones": [...]
    }
  ]
}
```

#### Get Transaction Details

Get details of a specific transaction.

**Endpoint:** `GET /api/transactions/{id}/`

**Response:** (200 OK)
```json
{
  "id": 1,
  "title": "Website Development Project",
  "total_value": "800.00",
  "buyer": {...},
  "seller": {...},
  "status": "IN_ESCROW",
  "created_at": "2025-11-13T15:00:00Z",
  "milestones": [...]
}
```

#### Fund Transaction

Transfer funds from buyer's wallet to escrow.

**Endpoint:** `POST /api/transactions/{id}/fund/`

**Authorization:** Only the buyer can fund the transaction.

**Preconditions:**
- Transaction status must be `PENDING_FUNDING`
- Buyer must have sufficient wallet balance

**Response:** (200 OK)
```json
{
  "id": 1,
  "title": "Website Development Project",
  "total_value": "800.00",
  "status": "IN_ESCROW",
  ...
}
```

**Error Responses:**
- `403 Forbidden`: User is not the buyer
- `400 Bad Request`: Insufficient funds or invalid status

### Milestones

#### List Milestones

Get all milestones for transactions involving the authenticated user.

**Endpoint:** `GET /api/milestones/`

**Response:** (200 OK)
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "transaction": 1,
      "title": "Design Phase",
      "description": "Create initial designs",
      "value": "300.00",
      "status": "PENDING",
      "submission_details": ""
    },
    ...
  ]
}
```

#### Submit Work

Seller submits work for a milestone.

**Endpoint:** `POST /api/milestones/{id}/submit/`

**Authorization:** Only the seller can submit work.

**Request Body:**
```json
{
  "submission_details": "Design mockups completed and uploaded to shared drive"
}
```

**Preconditions:**
- Milestone status must be `PENDING` or `REVISION_REQUESTED`

**Response:** (200 OK)
```json
{
  "id": 1,
  "transaction": 1,
  "title": "Design Phase",
  "value": "300.00",
  "status": "AWAITING_REVIEW",
  "submission_details": "Design mockups completed and uploaded to shared drive"
}
```

#### Approve Milestone

Buyer approves milestone and releases payment to seller.

**Endpoint:** `POST /api/milestones/{id}/approve/`

**Authorization:** Only the buyer can approve.

**Preconditions:**
- Milestone status must be `AWAITING_REVIEW`

**Response:** (200 OK)
```json
{
  "id": 1,
  "transaction": 1,
  "title": "Design Phase",
  "value": "300.00",
  "status": "COMPLETED",
  "submission_details": "Design mockups completed..."
}
```

**Side Effects:**
- Payment released to seller's wallet
- If all milestones completed, transaction status changes to `COMPLETED`

#### Request Revision

Buyer requests revision on submitted work.

**Endpoint:** `POST /api/milestones/{id}/request_revision/`

**Authorization:** Only the buyer can request revisions.

**Preconditions:**
- Milestone status must be `AWAITING_REVIEW`

**Response:** (200 OK)
```json
{
  "id": 1,
  "transaction": 1,
  "title": "Design Phase",
  "value": "300.00",
  "status": "REVISION_REQUESTED",
  "submission_details": "Design mockups completed..."
}
```

### Wallets

#### View Wallet

Get the authenticated user's wallet information.

**Endpoint:** `GET /api/wallets/`

**Response:** (200 OK)
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "username": "buyer_user",
        "email": "buyer@example.com"
      },
      "balance": "1000.00"
    }
  ]
}
```

## Status Flow

### Transaction Status Flow

1. `PENDING_FUNDING` - Initial state after creation
2. `IN_ESCROW` - After buyer funds the transaction
3. `COMPLETED` - All milestones completed
4. `DISPUTED` - Transaction disputed (future feature)
5. `CLOSED` - Transaction closed (future feature)

### Milestone Status Flow

1. `PENDING` - Initial state
2. `AWAITING_REVIEW` - Seller submitted work
3. `REVISION_REQUESTED` - Buyer requests changes
4. `COMPLETED` - Buyer approved, payment released
5. `DISPUTED` - Milestone disputed (future feature)

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid input or business logic violation
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - User not authorized for this action
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error responses include descriptive messages:

```json
{
  "error": "Only the buyer can fund this transaction."
}
```

## Example Usage Flow

1. **Buyer creates transaction**
   ```
   POST /api/transactions/
   ```

2. **Buyer funds transaction**
   ```
   POST /api/transactions/1/fund/
   ```

3. **Seller submits work**
   ```
   POST /api/milestones/1/submit/
   ```

4. **Buyer approves milestone**
   ```
   POST /api/milestones/1/approve/
   ```

5. **Repeat steps 3-4 for all milestones**

6. **Transaction automatically completes when all milestones are done**

## Testing

To run the test suite:

```bash
cd backend
python manage.py test
```

## Development Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. Create test users:
   ```bash
   python manage.py createsuperuser
   ```

4. Start development server:
   ```bash
   python manage.py runserver
   ```

5. Access admin panel at `http://localhost:8000/admin/`
