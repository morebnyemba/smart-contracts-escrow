from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BuyerTransactionViewSet

router = DefaultRouter()
router.register(r'my-transactions', BuyerTransactionViewSet, basename='my-transactions')

urlpatterns = [
    path('', include(router.urls)),
]
