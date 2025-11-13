# Smart Contracts Escrow Platform

This is a monorepo for a button-driven escrow platform, featuring a Django backend and a Next.js frontend.

## Project Context

The platform combines a simple, 8-step user flow with the ability to manage complex, milestone-based payments. It includes distinct portals for Buyers and Sellers, a seller onboarding/verification process, and seller discovery features.

## Repository Structure

- **backend**: Django project for the API, user management, transactions, and wallets.
- **frontend**: Next.js project for the user interface, including buyer/seller portals, onboarding, and transaction views.

## Features Implemented

### Core Transaction Flow (Phase 1-3) ✅

The platform now includes a complete, working transaction flow:

- ✅ **Transaction Creation**: Buyers can create escrow transactions with multiple milestones
- ✅ **Wallet-Based Funding**: Secure funding system with balance validation
- ✅ **Milestone Management**: Full lifecycle support (submission, approval, revision requests)
- ✅ **Payment Release**: Automatic fund release to sellers upon milestone approval
- ✅ **Transaction Completion**: Auto-completion when all milestones are done

### API Endpoints

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete API documentation.

Key endpoints:
- `POST /api/transactions/` - Create transaction
- `POST /api/transactions/{id}/fund/` - Fund transaction
- `POST /api/milestones/{id}/submit/` - Submit work
- `POST /api/milestones/{id}/approve/` - Approve milestone
- `POST /api/milestones/{id}/request_revision/` - Request revisions

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

6. Access the API at `http://localhost:8000/api/`
7. Access the admin panel at `http://localhost:8000/admin/`

### Running Tests

```bash
cd backend
python manage.py test
```

All 23 tests pass successfully, covering:
- Transaction creation and funding
- Milestone submission and approval
- Wallet operations
- User authorization

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Security

The implementation has been scanned with CodeQL and shows **0 security vulnerabilities**.

Security features include:
- Atomic database transactions for fund transfers
- User authorization checks (buyer/seller permissions)
- Status validation for all state transitions
- Input validation for all API endpoints

## Next Steps

- [ ] Implement dispute resolution mechanism
- [ ] Add notification system
- [ ] Implement review system
- [ ] Add payment gateway integration
- [ ] Enhance seller discovery features
- [ ] Implement real-time updates with WebSockets