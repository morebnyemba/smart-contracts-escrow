from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SellerProfileViewSet, ServiceCategoryViewSet, RegisterView

router = DefaultRouter()
router.register(r'sellers', SellerProfileViewSet, basename='seller')
router.register(r'categories', ServiceCategoryViewSet, basename='category')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('', include(router.urls)),
]
