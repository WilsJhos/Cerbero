from django.urls import path
from . import views

urlpatterns = [
    path('<str:slug>/', views.project_view, name='project-view'),
    path('<str:slug>/info/', views.get_project_info, name='project-info'),
    path('api/upload/', views.upload_file, name='upload-file'),
]