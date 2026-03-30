from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import json

@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    """Registro de nuevos usuarios"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Usuario y contraseña requeridos'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'El usuario ya existe'}, status=400)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        refresh = RefreshToken.for_user(user)
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    """Login de usuarios"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if not user:
            return JsonResponse({'error': 'Credenciales inválidas'}, status=401)
        
        refresh = RefreshToken.for_user(user)
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Obtener información del usuario autenticado"""
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'bio': user.bio,
        'avatar': user.avatar,
        'created_at': user.created_at
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout (invalida refresh token)"""
    try:
        data = json.loads(request.body)
        refresh_token = data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'success': True})
    except Exception as e:
        return Response({'error': str(e)}, status=400)