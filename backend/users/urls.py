from django.urls import path
from .views import SellerProfileLookupView

urlpatterns = [
    path('sellers/<uuid:public_seller_id>/', SellerProfileLookupView.as_view(), name='seller-lookup'),
]
