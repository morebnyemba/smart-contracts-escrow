from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import SellerProfile, ServiceCategory
from .serializers import SellerProfileSerializer, ServiceCategorySerializer


class SellerProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing seller profiles.
    Supports filtering by verification status and searching by username, company name, or skills.
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
            skill_ids = [s for s in skill_list if s.isdigit()]
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

