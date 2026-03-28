from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views


urlpatterns = [
    path('', core_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('p/', include('projects.urls')),
    path('api/', include('core.urls')),
    path('api/auth/', include('users.urls')),
    path('health/', views.health_check, name='health-check'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)