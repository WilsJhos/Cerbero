from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
import json

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Registro de nuevos usuarios"""
    data = json.loads(request.body)
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not password:
        return Response({'error': 'Usuario y contraseña requeridos'}, status=400)
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'El usuario ya existe'}, status=400)
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        },
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login de usuarios"""
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response({'error': 'Credenciales inválidas'}, status=401)
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        },
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    })

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