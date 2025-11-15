from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    SellerProfileViewSet, 
    ServiceCategoryViewSet, 
    SellerOnboardingView,
    RegisterView,
    LoginView,
    CurrentUserView
)

router = DefaultRouter()
router.register(r'sellers', SellerProfileViewSet, basename='seller')
router.register(r'categories', ServiceCategoryViewSet, basename='category')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/user/', CurrentUserView.as_view(), name='auth-user'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Seller endpoints
    path('onboarding/seller/', SellerOnboardingView.as_view(), name='seller-onboarding'),
    path('', include(router.urls)),
]
