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

#### Accept Transaction

Seller accepts the transaction terms, moving it from PENDING_FUNDING to AWAITING_PAYMENT status.

**Endpoint:** `POST /api/transactions/{id}/accept/`

**Authorization:** Only the seller can accept the transaction.

**Preconditions:**
- Transaction status must be `PENDING_FUNDING`

**Response:** (200 OK)
```json
{
  "id": 1,
  "title": "Website Development Project",
  "total_value": "800.00",
  "status": "AWAITING_PAYMENT",
  ...
}
```

**Side Effects:**
- Both buyer and seller are notified of the status change

**Error Responses:**
- `403 Forbidden`: User is not the seller
- `400 Bad Request`: Invalid transaction status

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

#### Open Dispute

Buyer opens a dispute on a milestone, triggering admin mediation.

**Endpoint:** `POST /api/milestones/{id}/dispute/`

**Authorization:** Only the buyer can open disputes.

**Preconditions:**
- Milestone status must NOT be `COMPLETED` or already `DISPUTED`

**Response:** (200 OK)
```json
{
  "id": 1,
  "transaction": 1,
  "title": "Design Phase",
  "value": "300.00",
  "status": "DISPUTED",
  "submission_details": "Design mockups completed..."
}
```

**Side Effects:**
- Milestone status changes to `DISPUTED`
- Parent transaction status changes to `DISPUTED`
- Admin is notified for mediation

**Error Responses:**
- `403 Forbidden`: User is not the buyer
- `400 Bad Request`: Milestone is already completed or disputed

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

### Reviews

#### Leave Review

Submit a review for a completed transaction. Both buyer and seller can leave reviews.

**Endpoint:** `POST /api/transactions/{id}/leave_review/`

**Authorization:** Only the buyer or seller of the transaction can leave a review.

**Request Body:**
```json
{
  "rating": 5,
  "comment": "Great work! Very professional and delivered on time."
}
```

**Preconditions:**
- Transaction status must be `COMPLETED` or `CLOSED`
- User must be either the buyer or seller
- User has not already reviewed this transaction

**Response:** (201 Created)
```json
{
  "id": 1,
  "transaction": 1,
  "reviewer": {
    "id": 1,
    "username": "buyer_user",
    "email": "buyer@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "rating": 5,
  "comment": "Great work! Very professional and delivered on time.",
  "created_at": "2025-11-15T10:00:00Z"
}
```

**Side Effects:**
- Transaction status changes to `CLOSED`

**Error Responses:**
- `400 Bad Request`: 
  - Rating not between 1-5
  - User has already reviewed this transaction
  - Transaction is not in COMPLETED status
- `404 Not Found`: Transaction doesn't exist or user is not involved in it

**Notes:**
- The `comment` field is optional
- Rating must be an integer between 1 and 5 (inclusive)
- Each user (buyer and seller) can only leave one review per transaction
- Transaction status changes to CLOSED after the first review is submitted
- Both parties can still leave reviews even after status is CLOSED

## Status Flow

### Transaction Status Flow

1. `PENDING_FUNDING` - Initial state after creation
2. `IN_ESCROW` - After buyer funds the transaction
3. `COMPLETED` - All milestones completed
4. `DISPUTED` - Buyer opened a dispute, requires admin mediation
5. `CLOSED` - Transaction closed (future feature)

### Milestone Status Flow

1. `PENDING` - Initial state
2. `AWAITING_REVIEW` - Seller submitted work
3. `REVISION_REQUESTED` - Buyer requests changes
4. `COMPLETED` - Buyer approved, payment released
5. `DISPUTED` - Buyer opened a dispute, requires admin mediation

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

### Happy Path

1. **Buyer creates transaction**
   ```
   POST /api/transactions/
   ```

2. **Seller accepts transaction**
   ```
   POST /api/transactions/1/accept/
   ```

3. **Buyer funds transaction**
   ```
   POST /api/transactions/1/fund/
   ```

4. **Seller submits work**
   ```
   POST /api/milestones/1/submit/
   ```

5. **Buyer approves milestone**
   ```
   POST /api/milestones/1/approve/
   ```

6. **Repeat steps 4-5 for all milestones**

7. **Transaction automatically completes when all milestones are done**

### Dispute Flow

1. **Buyer creates and funds transaction** (steps 1-2 from happy path)

2. **Seller submits work**
   ```
   POST /api/milestones/1/submit/
   ```

3. **Buyer opens dispute** (if not satisfied with work)
   ```
   POST /api/milestones/1/dispute/
   ```

4. **Admin is notified and begins mediation**

7. **Buyer and seller leave reviews**
   ```
   POST /api/transactions/1/leave_review/
   ```

8. **Transaction automatically closes after first review is submitted**

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
