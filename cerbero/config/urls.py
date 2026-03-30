from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views
from django.views.generic import TemplateView

urlpatterns = [
    path('', core_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('p/', include('projects.urls')),  # 👈 AGREGAR
    path('terms/', TemplateView.as_view(template_name='core/terms.html'), name='terms'),
    path('privacy/', TemplateView.as_view(template_name='core/privacy.html'), name='privacy'),
    path('cookies/', TemplateView.as_view(template_name='core/cookies.html'), name='cookies'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)