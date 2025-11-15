from rest_framework import generics, status
from rest_framework.response import Response
from users.models import SellerProfile, ServiceCategory
from .serializers import SellerProfileSerializer


class SellerSearchView(generics.ListAPIView):
    """
    API endpoint to search for verified sellers by skill.
    
    Query Parameters:
    - skill: The slug of the skill/service category to filter by
    
    Returns:
    - List of verified seller profiles matching the skill
    """
    serializer_class = SellerProfileSerializer
    
    def get_queryset(self):
        queryset = SellerProfile.objects.filter(
            verification_status=SellerProfile.VerificationStatus.VERIFIED
        )
        
        skill_slug = self.request.query_params.get('skill', None)
        if skill_slug:
            queryset = queryset.filter(skills__slug=skill_slug).distinct()
        
        return queryset.select_related('user').prefetch_related('skills')
    
    def list(self, request, *args, **kwargs):
        skill_slug = request.query_params.get('skill', None)
        
        if not skill_slug:
            return Response(
                {'error': 'skill query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify the skill exists
        if not ServiceCategory.objects.filter(slug=skill_slug).exists():
            return Response(
                {'error': f'Skill "{skill_slug}" not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return super().list(request, *args, **kwargs)
