from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Authentication
    path('auth/register/', views.register, name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/user/', views.current_user, name='current_user'),
    
    # Seller Onboarding
    path('seller/profile/', views.SellerProfileView.as_view(), name='seller_profile'),
    path('seller/profile/create/', views.SellerProfileCreateView.as_view(), name='seller_profile_create'),
    
    # Service Categories
    path('categories/', views.service_categories, name='service_categories'),
]
