from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from projects.models import Project

def home(request):
    """Vista principal - Devuelve el HTML"""
    return render(request, 'core/home.html')

@api_view(['GET'])
def health_check(request):
    return Response({
        'status': 'ok',
        'message': 'Cerbero API funcionando 🐕',
        'version': '1.0.0'
    })