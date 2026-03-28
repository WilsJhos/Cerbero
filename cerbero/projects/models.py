from django.db import models
from django.conf import settings
import secrets
import string
from datetime import datetime, timedelta

def generate_slug():
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(6))

class Project(models.Model):
    EXPIRATION_CHOICES = [
        (None, 'Nunca'),
        (24, '24 horas'),
        (168, '7 días'),
        (720, '30 días'),
    ]
    
    slug = models.CharField(max_length=10, unique=True, default=generate_slug)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    views = models.IntegerField(default=0)
    
    def __str__(self):
        return self.slug
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug()
        super().save(*args, **kwargs)
    
    def is_expired(self):
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False
    
    def get_expiration_display(self):
        if not self.expires_at:
            return "Nunca expira"
        days = (self.expires_at - self.created_at).days
        if days == 1:
            return "24 horas"
        elif days == 7:
            return "7 días"
        elif days == 30:
            return "30 días"
        return f"{days} días"

class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='projects/%Y/%m/%d/')
    original_name = models.CharField(max_length=255)
    size = models.IntegerField()
    file_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.original_name} ({self.size} bytes)"