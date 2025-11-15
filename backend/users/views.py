from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Q
from django.core.mail import mail_admins
from .models import SellerProfile, ServiceCategory
from .serializers import SellerProfileSerializer, ServiceCategorySerializer, SellerOnboardingSerializer


class SellerProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing seller profiles.
    Supports filtering by verification status and specific skills (using the `?skills=` parameter with comma-separated skill IDs or slugs), and searching by username, company name, or skill names (using the `?search=` parameter).
    """
    queryset = SellerProfile.objects.select_related('user').prefetch_related('skills').order_by('-id')
    serializer_class = SellerProfileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'company_name', 'skills__name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by verification status
        verification_status = self.request.query_params.get('verification_status', None)
        if verification_status:
            queryset = queryset.filter(verification_status=verification_status)
        
        # Filter by skills (comma-separated skill IDs or slugs)
        skills = self.request.query_params.get('skills', None)
        if skills:
            skill_list = [s.strip() for s in skills.split(',')]
            # Check if they are numeric IDs or slugs
            skill_ids = [int(s) for s in skill_list if s.isdigit()]
            skill_slugs = [s for s in skill_list if not s.isdigit()]
            
            q_filter = Q()
            if skill_ids:
                q_filter |= Q(skills__id__in=skill_ids)
            if skill_slugs:
                q_filter |= Q(skills__slug__in=skill_slugs)
            
            if q_filter:
                queryset = queryset.filter(q_filter).distinct()
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def verified(self, request):
        """Get only verified sellers"""
        verified_sellers = self.get_queryset().filter(
            verification_status=SellerProfile.VerificationStatus.VERIFIED
        )
        page = self.paginate_queryset(verified_sellers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(verified_sellers, many=True)
        return Response(serializer.data)


class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing service categories.
    """
    queryset = ServiceCategory.objects.order_by('name')
    serializer_class = ServiceCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug']


class SellerOnboardingView(APIView):
    """
    API endpoint for seller onboarding.
    Allows authenticated users to create or update their seller profile.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create or update seller profile for the authenticated user"""
        user = request.user
        
        try:
            # Check if seller profile already exists
            seller_profile = SellerProfile.objects.get(user=user)
            serializer = SellerOnboardingSerializer(seller_profile, data=request.data, partial=True)
            is_update = True
        except SellerProfile.DoesNotExist:
            serializer = SellerOnboardingSerializer(data=request.data)
            is_update = False
        
        if serializer.is_valid():
            if is_update:
                seller_profile = serializer.save()
            else:
                seller_profile = serializer.save(user=user)
            
            # Notify admin if verification document was submitted and status is PENDING
            if seller_profile.verification_document and seller_profile.verification_status == SellerProfile.VerificationStatus.PENDING:
                try:
                    mail_admins(
                        subject='New Seller Verification Submission',
                        message=f'User {user.username} ({user.email}) has submitted a seller profile for verification.\n\n'
                                f'Profile ID: {seller_profile.id}\n'
                                f'Account Type: {seller_profile.account_type}\n'
                                f'Company Name: {seller_profile.company_name or "N/A"}\n\n'
                                f'Please review the submission in the admin panel.',
                    )
                except Exception as e:
                    # Log the error but don't fail the request
                    pass
            
            return Response(serializer.data, status=status.HTTP_200_OK if is_update else status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

