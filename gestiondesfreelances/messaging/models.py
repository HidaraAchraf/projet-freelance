from django.db import models
from django.utils import timezone
from accounts.models import User
from projects.models import Project

class Conversation(models.Model):
    participants = models.ManyToManyField(
        User, 
        related_name='conversations',
        verbose_name='Participants'
    )
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='conversations', 
        null=True, 
        blank=True,
        verbose_name='Projet associé'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Date de mise à jour'
    )

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'

    def __str__(self):
        participants_names = ", ".join([user.get_full_name() or user.username for user in self.participants.all()])
        project_info = f" (Projet: {self.project.title})" if self.project else ""
        return f"Conversation entre {participants_names}{project_info}"

    def get_other_participant(self, user):
        """Retourne l'autre participant de la conversation"""
        return self.participants.exclude(id=user.id).first()

    def get_unread_count(self, user):
        """Retourne le nombre de messages non lus pour un utilisateur"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()

class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages',
        verbose_name='Conversation'
    )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        verbose_name='Expéditeur'
    )
    content = models.TextField(
        verbose_name='Contenu'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'envoi'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Lu'
    )

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f"Message de {self.sender.get_full_name() or self.sender.username} ({self.timestamp.strftime('%d/%m/%Y %H:%M')})"

    def mark_as_read(self):
        """Marque le message comme lu"""
        if not self.is_read:
            self.is_read = True
            self.save()

    def get_short_content(self, length=50):
        """Retourne un contenu tronqué pour l'affichage"""
        if len(self.content) > length:
            return self.content[:length] + '...'
        return self.content