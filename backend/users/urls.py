from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SellerProfileViewSet, ServiceCategoryViewSet, SellerOnboardingView

router = DefaultRouter()
router.register(r'sellers', SellerProfileViewSet, basename='seller')
router.register(r'categories', ServiceCategoryViewSet, basename='category')

urlpatterns = [
    path('onboarding/seller/', SellerOnboardingView.as_view(), name='seller-onboarding'),
    path('', include(router.urls)),
]
