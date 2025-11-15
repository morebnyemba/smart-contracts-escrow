from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser
from wallets.models import UserWallet, EscrowWallet, PaymentTransaction
from transactions.models import EscrowTransaction
from decimal import Decimal

class PaymentWebhookTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('payment_webhook')
        
        # Create test users
        self.buyer = CustomUser.objects.create_user(
            username='buyer1',
            email='buyer@test.com',
            password='testpass123'
        )
        self.seller = CustomUser.objects.create_user(
            username='seller1',
            email='seller@test.com',
            password='testpass123'
        )
        
        # Create user wallet with balance
        self.buyer_wallet = UserWallet.objects.create(
            user=self.buyer,
            balance=Decimal('1000.00')
        )
        
        # Create escrow transaction
        self.escrow_transaction = EscrowTransaction.objects.create(
            title='Test Project',
            total_value=Decimal('500.00'),
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.PENDING_FUNDING
        )
    
    def test_successful_payment(self):
        """Test successful payment processing"""
        payload = {
            'transaction_id': self.escrow_transaction.id,
            'user_id': self.buyer.id,
            'amount': '500.00'
        }
        
        response = self.client.post(self.url, payload, format='json')
        
        if response.status_code != status.HTTP_200_OK:
            print(f"Error response: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify wallet balances
        self.buyer_wallet.refresh_from_db()
        self.assertEqual(self.buyer_wallet.balance, Decimal('500.00'))
        
        escrow_wallet = EscrowWallet.objects.get(id=1)
        self.assertEqual(escrow_wallet.balance, Decimal('500.00'))
        
        # Verify transaction status
        self.escrow_transaction.refresh_from_db()
        self.assertEqual(self.escrow_transaction.status, EscrowTransaction.TransactionStatus.IN_ESCROW)
        
        # Verify payment transaction
        payment_txn = PaymentTransaction.objects.get(id=response.data['payment_transaction_id'])
        self.assertEqual(payment_txn.status, PaymentTransaction.PaymentStatus.COMPLETED)
        self.assertIsNotNone(payment_txn.completed_at)
    
    def test_insufficient_balance(self):
        """Test payment with insufficient balance"""
        payload = {
            'transaction_id': self.escrow_transaction.id,
            'user_id': self.buyer.id,
            'amount': '2000.00'  # More than wallet balance
        }
        
        # Update transaction value to match
        self.escrow_transaction.total_value = Decimal('2000.00')
        self.escrow_transaction.save()
        
        response = self.client.post(self.url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient balance', response.data['error'])
    
    def test_missing_fields(self):
        """Test payment with missing required fields"""
        payload = {
            'transaction_id': self.escrow_transaction.id,
            # Missing user_id and amount
        }
        
        response = self.client.post(self.url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Missing required fields', response.data['error'])
    
    def test_invalid_amount(self):
        """Test payment with invalid amount"""
        payload = {
            'transaction_id': self.escrow_transaction.id,
            'user_id': self.buyer.id,
            'amount': 'invalid'
        }
        
        response = self.client.post(self.url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid amount format', response.data['error'])
    
    def test_negative_amount(self):
        """Test payment with negative amount"""
        payload = {
            'transaction_id': self.escrow_transaction.id,
            'user_id': self.buyer.id,
            'amount': '-100.00'
        }
        
        response = self.client.post(self.url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Amount must be positive', response.data['error'])
    
    def test_nonexistent_user_wallet(self):
        """Test payment with nonexistent user wallet"""
        payload = {
            'transaction_id': self.escrow_transaction.id,
            'user_id': 99999,  # Non-existent user
            'amount': '500.00'
        }
        
        response = self.client.post(self.url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('User wallet not found', response.data['error'])
    
    def test_nonexistent_transaction(self):
        """Test payment with nonexistent transaction"""
        payload = {
            'transaction_id': 99999,  # Non-existent transaction
            'user_id': self.buyer.id,
            'amount': '500.00'
        }
        
        response = self.client.post(self.url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Escrow transaction', response.data['error'])
    
    def test_amount_mismatch(self):
        """Test payment with amount not matching transaction value"""
        payload = {
            'transaction_id': self.escrow_transaction.id,
            'user_id': self.buyer.id,
            'amount': '300.00'  # Different from transaction value of 500
        }
        
        response = self.client.post(self.url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('does not match transaction value', response.data['error'])
