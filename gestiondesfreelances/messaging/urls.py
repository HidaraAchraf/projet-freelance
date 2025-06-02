from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Liste des conversations (boîte de réception)
    path('inbox/', views.inbox, name='inbox'),
    
    # Détail d'une conversation
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation'),
    
    # Démarrer une nouvelle conversation avec un utilisateur spécifique
    path('new/user/<int:user_id>/', views.start_conversation, name='new_user_conversation'),
    
    # Démarrer une nouvelle conversation liée à un projet (avec le client par défaut)
    path('new/project/<int:project_id>/', views.start_conversation, name='new_project_conversation'),
    
    # Démarrer une nouvelle conversation (sans destinataire spécifié)
    path('new/', views.start_conversation, name='new_conversation'),
    
]