from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BuyerTransactionViewSet, SellerTransactionViewSet

router = DefaultRouter()
router.register(r'my-transactions', BuyerTransactionViewSet, basename='my-transactions')
router.register(r'seller', SellerTransactionViewSet, basename='seller')

urlpatterns = [
    path('', include(router.urls)),
]
