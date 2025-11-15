# API Documentation

## Buyer Portal API Endpoints

### My Transactions

Retrieve transactions where the authenticated user is the buyer.

#### List Transactions

**Endpoint:** `GET /api/buyer/my-transactions/`

**Authentication:** Required (Session-based)

**Permissions:** IsAuthenticated

**Response:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Website Development Project",
      "total_value": "2500.00",
      "buyer": 1,
      "buyer_name": "john_buyer",
      "seller": 2,
      "seller_name": "jane_seller",
      "status": "IN_ESCROW",
      "created_at": "2025-11-13T15:24:00Z",
      "milestones": [
        {
          "id": 1,
          "title": "Design Phase",
          "description": "Complete UI/UX design",
          "value": "800.00",
          "status": "COMPLETED",
          "submission_details": ""
        },
        {
          "id": 2,
          "title": "Development Phase",
          "description": "Build frontend and backend",
          "value": "1700.00",
          "status": "PENDING",
          "submission_details": ""
        }
      ]
    }
  ]
}
```

**Features:**
- Returns transactions ordered by most recent first
- Includes nested milestone details
- Pagination enabled (20 items per page)
- Only returns transactions where the user is the buyer

#### Retrieve Transaction Detail

**Endpoint:** `GET /api/buyer/my-transactions/{id}/`

**Authentication:** Required (Session-based)

**Permissions:** IsAuthenticated

**Response:** Same as individual transaction object in list view

**Error Responses:**
- `403 Forbidden`: User is not authenticated
- `404 Not Found`: Transaction doesn't exist or user is not the buyer

#### Transaction Status Values

- `PENDING_FUNDING`: Awaiting initial funding
- `AWAITING_PAYMENT`: Waiting for payment
- `IN_ESCROW`: Funds are in escrow
- `WORK_IN_PROGRESS`: Work is being done
- `COMPLETED`: Transaction completed
- `DISPUTED`: Transaction is disputed
- `CLOSED`: Transaction closed

#### Milestone Status Values

- `PENDING`: Milestone not started
- `AWAITING_REVIEW`: Submitted for review
- `REVISION_REQUESTED`: Needs revisions
- `COMPLETED`: Milestone completed
- `DISPUTED`: Milestone disputed

## Security

- All endpoints require authentication
- Users can only access their own transactions
- Endpoints are read-only (POST/PUT/DELETE not allowed)
- Cross-buyer access is prevented
