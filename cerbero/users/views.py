from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User
from projects.models import Project

def profile_page(request):
    return render(request, 'core/profile.html')

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Obtener o actualizar perfil del usuario"""
    user = request.user
    
    if request.method == 'GET':
        # Estadísticas del usuario
        projects_count = Project.objects.filter(user=user).count()
        total_views = sum(p.views for p in Project.objects.filter(user=user))
        total_files = sum(p.files.count() for p in Project.objects.filter(user=user))
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'bio': user.bio,
            'avatar': user.avatar,
            'created_at': user.created_at,
            'stats': {
                'projects': projects_count,
                'views': total_views,
                'files': total_files
            }
        })
    
    elif request.method == 'PUT':
        import json
        data = json.loads(request.body)
        user.bio = data.get('bio', user.bio)
        user.avatar = data.get('avatar', user.avatar)
        user.save()
        
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'bio': user.bio,
                'avatar': user.avatar
            }
        })

        