import os
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Project, ProjectFile

def project_view(request, slug):
    """Vista pública del proyecto"""
    project = get_object_or_404(Project, slug=slug)
    files = project.files.all()
    
    # Incrementar contador de vistas
    project.views += 1
    project.save()
    
    # Modo IA (texto plano)
    if request.GET.get('mode') == 'ia' or request.GET.get('mode') == 'text':
        response = HttpResponse(content_type='text/plain; charset=utf-8')
        response.write(f"PROYECTO: {project.slug}\n")
        response.write(f"ARCHIVOS: {files.count()}\n")
        response.write("=" * 50 + "\n\n")
        
        for file in files:
            response.write(f"=== {file.original_name} ===\n")
            response.write(f"Tamaño: {file.size} bytes\n")
            response.write(f"Tipo: {file.file_type}\n")
            response.write("-" * 30 + "\n")
            
            try:
                with open(file.file.path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    response.write(content)
            except (UnicodeDecodeError, FileNotFoundError, OSError):
                response.write("[ARCHIVO BINARIO - No se puede mostrar en texto plano]")
            response.write("\n\n" + "=" * 50 + "\n\n")
        
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
        if slug:
            project = Project.objects.get(slug=slug)
        else:
            project = Project.objects.create()
        
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
            'count': len(uploaded_files)
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
        'created_at': project.created_at.isoformat(),
        'views': project.views,
        'files': [{
            'name': f.original_name,
            'size': f.size,
            'type': f.file_type,
            'url': f.file.url
        } for f in files]
    })