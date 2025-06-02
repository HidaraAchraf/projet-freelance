from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    CLIENT = 'CL'
    FREELANCER = 'FL'
    USER_TYPE_CHOICES = [
        (CLIENT, 'Client'),
        (FREELANCER, 'Freelancer'),
    ]
    
    user_type = models.CharField(max_length=2, choices=USER_TYPE_CHOICES, default=CLIENT)
    phone_number = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class FreelancerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelancer_profile')
    skills = models.TextField(help_text="Listez vos compétences séparées par des virgules")
    hourly_rate = models.DecimalField(default=False,max_digits=10, decimal_places=2)
    bio = models.TextField(blank=True)
    portfolio_url = models.URLField(blank=True)
    rating = models.FloatField(default=0.0)
    completed_projects = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Profil de {self.user.username}"


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    company = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    posted_projects = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Profil client de {self.user.username}"
