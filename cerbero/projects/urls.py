from django.urls import path
from . import views

urlpatterns = [
    path('<str:slug>/', views.project_view, name='project-view'),
    path('<str:slug>/info/', views.get_project_info, name='project-info'),
    path('<str:slug>/update/', views.update_project, name='update-project'),
    path('<str:slug>/delete/', views.delete_project, name='delete-project'),
    path('api/upload/', views.upload_file, name='upload-file'),
    path('api/my-projects/', views.my_projects, name='my-projects'),
]