from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MyProjectsViewSet

router = DefaultRouter()
router.register(r'my-projects', MyProjectsViewSet, basename='my-projects')

urlpatterns = [
    path('', include(router.urls)),
]
