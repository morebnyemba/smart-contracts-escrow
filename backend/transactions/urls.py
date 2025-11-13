from django.urls import path
from .views import MyTransactionsView

urlpatterns = [
    path('my-transactions/', MyTransactionsView.as_view(), name='my-transactions'),
]
