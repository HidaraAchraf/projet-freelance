from django.db import models
from django.utils import timezone
from accounts.models import User
from projects.models import Project

class Bid(models.Model):
    PENDING = 'PE'
    ACCEPTED = 'AC'
    REJECTED = 'RE'
    WITHDRAWN = 'WI'
    
    STATUS_CHOICES = [
        (PENDING, 'En attente'),
        (ACCEPTED, 'Acceptée'),
        (REJECTED, 'Rejetée'),
        (WITHDRAWN, 'Retirée'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bids')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    delivery_time = models.PositiveIntegerField(verbose_name="Délai (en jours)")
    proposal = models.TextField(verbose_name="Proposition")
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['project', 'freelancer']
    
    def __str__(self):
        return f"Offre #{self.id} - {self.freelancer.username} pour {self.project.title}"
    
    def accept(self):
        self.status = self.ACCEPTED
        self.save()
        self.project.status = Project.IN_PROGRESS
        self.project.save()
    
    def reject(self):
        self.status = self.REJECTED
        self.save()
    
    def withdraw(self):
        self.status = self.WITHDRAWN
        self.save()
    
    def can_be_accepted(self):
        return self.status == self.PENDING
    
    def can_be_modified_by(self, user):
        return (
            user == self.freelancer and 
            self.status in [self.PENDING, self.ACCEPTED]
        )
    
    def can_be_viewed_by(self, user):
        return (
            user == self.freelancer or 
            user == self.project.client or
            user.is_superuser
        )