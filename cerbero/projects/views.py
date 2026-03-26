import os
import json
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Project, ProjectFile


def project_view(request, slug):
    """Vista pública del proyecto"""
    project = get_object_or_404(Project, slug=slug)
    
    # Verificar expiración
    if project.is_expired():
        return render(request, 'core/expired.html', {'project': project})
    
    files = project.files.all()
    
    # Incrementar contador de vistas
    project.views += 1
    project.save()
    
    # Modo IA (texto plano optimizado)
    if request.GET.get('mode') == 'ia' or request.GET.get('mode') == 'text':
        response = HttpResponse(content_type='text/plain; charset=utf-8')
        
        # Header con metadatos
        response.write(f"# PROYECTO: {project.title or project.slug}\n")
        response.write(f"# DESCRIPCIÓN: {project.description or 'Sin descripción'}\n")
        response.write(f"# ARCHIVOS: {files.count()}\n")
        response.write(f"# VISTAS: {project.views}\n")
        response.write(f"# CREADO: {project.created_at.strftime('%Y-%m-%d %H:%M')}\n")
        if project.expires_at:
            response.write(f"# EXPIRE: {project.expires_at.strftime('%Y-%m-%d %H:%M')}\n")
        response.write("=" * 60 + "\n\n")
        
        for file in files:
            response.write(f"## ARCHIVO: {file.original_name}\n")
            response.write(f"Tamaño: {file.size} bytes\n")
            response.write(f"Tipo: {file.file_type}\n")
            response.write("-" * 40 + "\n")
            
            try:
                with open(file.file.path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    response.write(content)
            except (UnicodeDecodeError, FileNotFoundError, OSError):
                response.write("[ARCHIVO BINARIO - No se puede mostrar en texto plano]")
            response.write("\n\n" + "=" * 60 + "\n\n")
        
        return response
    
    # Modo humano
    return render(request, 'core/project.html', {
        'project': project,
        'files': files,
        'total_size': sum(f.size for f in files)
    })


@csrf_exempt
@require_http_methods(["POST"])
def upload_file(request):
    """Endpoint para subir archivos"""
    try:
        slug = request.POST.get('slug')
        
        # Verificar si hay usuario autenticado
        user = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            from rest_framework_simplejwt.tokens import AccessToken
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                token = auth_header.split(' ')[1]
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                user = User.objects.get(id=user_id)
            except Exception as e:
                pass
        
        if slug:
            project = Project.objects.get(slug=slug)
        else:
            project = Project.objects.create(user=user)
        
        files = request.FILES.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file.size > 100 * 1024 * 1024:
                return JsonResponse({'error': f'Archivo {file.name} excede 100MB'}, status=400)
            
            project_file = ProjectFile.objects.create(
                project=project,
                file=file,
                original_name=file.name,
                size=file.size,
                file_type=file.content_type or 'application/octet-stream'
            )
            
            uploaded_files.append({
                'name': file.name,
                'size': file.size,
                'type': file.content_type,
                'url': project_file.file.url
            })
        
        return JsonResponse({
            'success': True,
            'slug': project.slug,
            'url': f'/p/{project.slug}/',
            'full_url': request.build_absolute_uri(f'/p/{project.slug}/'),
            'files': uploaded_files,
            'count': len(uploaded_files),
            'user': user.username if user else None
        })
        
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Proyecto no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_project_info(request, slug):
    """Obtener información del proyecto en JSON"""
    project = get_object_or_404(Project, slug=slug)
    files = project.files.all()
    
    return JsonResponse({
        'slug': project.slug,
        'title': project.title,
        'description': project.description,
        'created_at': project.created_at.isoformat(),
        'expires_at': project.expires_at.isoformat() if project.expires_at else None,
        'views': project.views,
        'files': [{
            'name': f.original_name,
            'size': f.size,
            'type': f.file_type,
            'url': f.file.url
        } for f in files]
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_projects(request):
    """Lista de proyectos del usuario autenticado"""
    projects = Project.objects.filter(user=request.user).order_by('-created_at')
    
    return Response({
        'projects': [{
            'slug': p.slug,
            'title': p.title or p.slug,
            'description': p.description,
            'created_at': p.created_at,
            'files_count': p.files.count(),
            'views': p.views,
            'url': f'/p/{p.slug}/'
        } for p in projects]
    })


@csrf_exempt
@require_http_methods(["PUT"])
def update_project(request, slug):
    """Actualizar título y descripción del proyecto"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    project = get_object_or_404(Project, slug=slug, user=request.user)
    
    try:
        data = json.loads(request.body)
        project.title = data.get('title', project.title)
        project.description = data.get('description', project.description)
        project.save()
        
        return JsonResponse({
            'success': True,
            'project': {
                'slug': project.slug,
                'title': project.title,
                'description': project.description
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_project(request, slug):
    """Eliminar proyecto y todos sus archivos"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    project = get_object_or_404(Project, slug=slug, user=request.user)
    
    # Eliminar archivos físicos
    for file in project.files.all():
        file.file.delete(save=False)
    
    # Eliminar proyecto
    project.delete()
    
    return JsonResponse({'success': True})