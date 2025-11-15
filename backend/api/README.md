# API Documentation

## Payment Webhook

### Endpoint
`POST /api/webhook/payment/`

### Description
Processes payment and moves funds from a user's wallet to the escrow wallet. This endpoint is used when a buyer confirms payment for an escrow transaction.

### Request Body
```json
{
  "transaction_id": 1,
  "user_id": 1,
  "amount": "1000.00"
}
```

**Parameters:**
- `transaction_id` (integer, required): The ID of the escrow transaction
- `user_id` (integer, required): The ID of the user making the payment
- `amount` (decimal string, required): The payment amount (must match transaction value)

### Success Response
**Code:** 200 OK

```json
{
  "success": true,
  "message": "Payment processed successfully",
  "payment_transaction_id": 1,
  "escrow_transaction_status": "IN_ESCROW",
  "user_wallet_balance": 4000.00,
  "escrow_wallet_balance": 1000.00
}
```

### Error Responses

**Missing Required Fields**
- **Code:** 400 Bad Request
- **Content:** `{"error": "Missing required fields: transaction_id, user_id, amount"}`

**Invalid Amount Format**
- **Code:** 400 Bad Request
- **Content:** `{"error": "Invalid amount format"}`

**Negative Amount**
- **Code:** 400 Bad Request
- **Content:** `{"error": "Amount must be positive"}`

**Amount Mismatch**
- **Code:** 400 Bad Request
- **Content:** `{"error": "Amount {amount} does not match transaction value {value}"}`

**Insufficient Balance**
- **Code:** 400 Bad Request
- **Content:** `{"error": "Insufficient balance. Required: {amount}, Available: {balance}"}`

**User Wallet Not Found**
- **Code:** 404 Not Found
- **Content:** `{"error": "User wallet not found for user {user_id}"}`

**Transaction Not Found**
- **Code:** 404 Not Found
- **Content:** `{"error": "Escrow transaction {transaction_id} not found"}`

**Server Error**
- **Code:** 500 Internal Server Error
- **Content:** `{"error": "Payment processing failed: {error_message}"}`

### Example Usage

```bash
curl -X POST http://localhost:8000/api/webhook/payment/ \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": 1,
    "user_id": 1,
    "amount": "1000.00"
  }'
```

### Transaction Flow
1. Validates all required fields are present
2. Validates amount format and is positive
3. Locks user wallet and escrow transaction for update (prevents race conditions)
4. Verifies amount matches transaction total value
5. Checks user has sufficient balance
6. Creates payment transaction record
7. Deducts amount from user wallet
8. Adds amount to escrow wallet
9. Updates payment transaction status to COMPLETED
10. Updates escrow transaction status to IN_ESCROW
11. Returns success response with updated balances

All operations are performed within a database transaction to ensure atomicity - either all steps succeed or all are rolled back.
