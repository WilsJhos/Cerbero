from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from projects.models import Project
from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health-check'),
    path('', views.home, name='api-home'),
] 

def home(request):
    """Vista principal de la landing page"""
    recent_projects = Project.objects.all().order_by('-created_at')[:5]
    
    return render(request, 'core/home.html', {
        'recent_projects': recent_projects,
    })

@api_view(['GET'])
def health_check(request):
    """Endpoint para verificar que la API funciona"""
    return Response({
        'status': 'ok',
        'message': 'Cerbero API funcionando 🐕',
        'version': '1.0.0'
    })