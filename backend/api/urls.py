from django.urls import path
from .views import SellerSearchView

app_name = 'api'

urlpatterns = [
    path('sellers/search/', SellerSearchView.as_view(), name='seller-search'),
]
