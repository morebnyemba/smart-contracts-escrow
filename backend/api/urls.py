from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EscrowTransactionViewSet, MilestoneViewSet, UserWalletViewSet

router = DefaultRouter()
router.register(r'transactions', EscrowTransactionViewSet, basename='transaction')
router.register(r'milestones', MilestoneViewSet, basename='milestone')
router.register(r'wallets', UserWalletViewSet, basename='wallet')

urlpatterns = [
    path('', include(router.urls)),
]
