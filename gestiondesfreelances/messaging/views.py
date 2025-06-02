from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.db.models import Q
from accounts.models import User
from projects.models import Project
from .models import Conversation, Message
from .forms import MessageForm

@login_required
def inbox(request):
    # Récupère toutes les conversations où l'utilisateur est participant
    conversations = Conversation.objects.filter(
        participants=request.user
    ).order_by('-updated_at').distinct()
    
    context = {
        'conversations': conversations,
        'unread_count': get_unread_count(request.user)
    }
    return render(request, 'messaging/inbox.html', context)

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation.objects.prefetch_related('participants', 'messages'),
        id=conversation_id,
        participants=request.user
    )
    
    # Marquer les messages non lus comme lus
    unread_messages = Message.objects.filter(
        conversation=conversation,
        is_read=False
    ).exclude(sender=request.user)
    
    if unread_messages.exists():
        unread_messages.update(is_read=True)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            
            # Mettre à jour la date de modification de la conversation
            conversation.save()
            
            django_messages.success(request, "Message envoyé!")
            return redirect('messaging:conversation', conversation_id=conversation.id)
    else:
        form = MessageForm()
    
    messages_list = conversation.messages.all().order_by('timestamp')
    
    # Récupérer l'autre participant (exclure l'utilisateur actuel)
    other_participant = conversation.participants.exclude(id=request.user.id).first()
    
    context = {
        'conversation': conversation,
        'messages': messages_list,
        'form': form,
        'other_participant': other_participant,
        'unread_count': get_unread_count(request.user),
        'project': conversation.project  # Ajout du projet au contexte
    }
    return render(request, 'messaging/conversation.html', context)

@login_required
def start_conversation(request, user_id=None, project_id=None):
    recipient = None
    project = None
    
    if user_id:
        recipient = get_object_or_404(User, id=user_id)
        # Vérifier que l'utilisateur ne démarre pas une conversation avec lui-même
        if recipient == request.user:
            django_messages.error(request, "Vous ne pouvez pas démarrer une conversation avec vous-même.")
            return redirect('messaging:inbox')
    
    if project_id:
        project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            
            # Trouver ou créer une conversation existante
            if recipient:
                # Conversation entre deux utilisateurs
                conversation = Conversation.objects.filter(
                    participants=request.user
                ).filter(
                    participants=recipient
                ).first()
                
                if not conversation:
                    conversation = Conversation.objects.create()
                    conversation.participants.add(request.user, recipient)
            elif project:
                # Conversation liée à un projet
                conversation = Conversation.objects.filter(
                    project=project,
                    participants=request.user
                ).first()
                
                if not conversation:
                    conversation = Conversation.objects.create(project=project)
                    # Ajouter l'utilisateur actuel et le client du projet
                    conversation.participants.add(request.user, project.client)
            
            # Créer le message
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            
            django_messages.success(request, "Conversation démarrée avec succès!")
            return redirect('messaging:conversation', conversation_id=conversation.id)
    else:
        form = MessageForm(initial={'content': ''})
    
    context = {
        'form': form,
        'recipient': recipient,
        'project': project,
        'unread_count': get_unread_count(request.user)
    }
    return render(request, 'messaging/new_conversation.html', context)

def get_unread_count(user):
    """Retourne le nombre de messages non lus pour l'utilisateur"""
    return Message.objects.filter(
        conversation__participants=user,
        is_read=False
    ).exclude(
        sender=user
    ).count()
