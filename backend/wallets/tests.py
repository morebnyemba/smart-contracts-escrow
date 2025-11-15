from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import UserWallet

User = get_user_model()


class UserWalletModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='password123'
        )

    def test_create_wallet(self):
        """Test creating a user wallet"""
        wallet = UserWallet.objects.create(user=self.user, balance=Decimal('100.00'))
        self.assertEqual(wallet.user, self.user)
        self.assertEqual(wallet.balance, Decimal('100.00'))

    def test_default_balance(self):
        """Test that default balance is 0.00"""
        wallet = UserWallet.objects.create(user=self.user)
        self.assertEqual(wallet.balance, Decimal('0.00'))

    def test_wallet_balance_update(self):
        """Test updating wallet balance"""
        wallet = UserWallet.objects.create(user=self.user, balance=Decimal('100.00'))
        
        # Add funds
        wallet.balance += Decimal('50.00')
        wallet.save()
        self.assertEqual(wallet.balance, Decimal('150.00'))
        
        # Deduct funds
        wallet.balance -= Decimal('30.00')
        wallet.save()
        self.assertEqual(wallet.balance, Decimal('120.00'))

    def test_one_wallet_per_user(self):
        """Test that each user can have only one wallet"""
        UserWallet.objects.create(user=self.user, balance=Decimal('100.00'))
        
        # Try to create another wallet for the same user should fail
        with self.assertRaises(Exception):
            UserWallet.objects.create(user=self.user, balance=Decimal('50.00'))
