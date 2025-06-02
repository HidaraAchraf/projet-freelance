from django.db import models
from accounts.models import User
from django.utils import timezone

class Project(models.Model):
    related_name='projects_client'
    OPEN = 'OP'
    IN_PROGRESS = 'IP'
    COMPLETED = 'CO'
    CANCELLED = 'CA'
    
    STATUS_CHOICES = [
        (OPEN, 'Open'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField()
    skills_required = models.CharField(max_length=255)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=OPEN)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    def mark_as_completed(self):
        self.status = self.COMPLETED
        self.completed_at = timezone.now()
        self.save()

    def __str__(self):
        return self.title    
    
    def __str__(self):
        return f"{self.title} (Client: {self.client.username})"
    
    def is_open(self):
        return self.status == self.OPEN
    
    def days_remaining(self):
        return (self.deadline - timezone.now().date()).days