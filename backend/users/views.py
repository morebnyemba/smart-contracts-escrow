from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import SellerProfile
from .serializers import SellerProfileSerializer


class SellerProfileLookupView(generics.RetrieveAPIView):
    """
    API endpoint to lookup a seller profile by public_seller_id.
    """
    serializer_class = SellerProfileSerializer
    lookup_field = 'public_seller_id'
    queryset = SellerProfile.objects.all()
