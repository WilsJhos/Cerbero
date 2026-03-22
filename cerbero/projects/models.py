from django.db import models
from django.conf import settings
import secrets
import string

def generate_slug():
    """Genera un slug único de 6 caracteres"""
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(6))

class Project(models.Model):
    slug = models.CharField(max_length=10, unique=True, default=generate_slug)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    views = models.IntegerField(default=0)
    
    def __str__(self):
        return self.slug

class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='projects/%Y/%m/%d/')
    original_name = models.CharField(max_length=255)
    size = models.IntegerField()
    file_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.original_name} ({self.size} bytes)"