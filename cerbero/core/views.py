# core/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.shortcuts import render
from projects.models import Project

def home(request):
    """Vista principal de la landing page"""
    # Obtener proyectos recientes (si hay usuarios logueados)
    recent_projects = Project.objects.all().order_by('-created_at')[:5]
    
    return render(request, 'core/home.html', {
        'recent_projects': recent_projects,
    })

@api_view(['GET'])
def health_check(request):
    """
    Endpoint para verificar que la API funciona
    """
    return Response({
        'status': 'ok',
        'message': 'Cerbero API funcionando 🐕',
        'version': '1.0.0'
    })

def home(request):
    """
    Vista simple para la raíz
    """
    return JsonResponse({
        'message': 'Bienvenido a Cerbero API',
        'docs': '/api/',
        'status': 'online'
    })