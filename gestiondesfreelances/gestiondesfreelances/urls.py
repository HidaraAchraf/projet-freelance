
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from accounts.views import register  # Importez la vue register depuis accounts

urlpatterns = [
    # Page d'accueil
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # Admin
    path('admin/', admin.site.urls),

    # Accounts
    path('accounts/', include('accounts.urls')),
    
    # Projects
    path('projects/', include('projects.urls')),
    
    # Bids
    path('bids/', include('bids.urls')),
    
    # Messaging
    path('messaging/', include('messaging.urls')),
    
]
