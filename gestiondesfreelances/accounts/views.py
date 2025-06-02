from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (UserRegisterForm, UserLoginForm, 
                   ProfileUpdateForm, FreelancerProfileForm, 
                   ClientProfileForm)
from .models import User, FreelancerProfile, ClientProfile



def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Créer le profil approprié
            if user.user_type == User.FREELANCER:
                # Créer un profil Freelance pour l'utilisateur
                FreelancerProfile.objects.create(user=user)
            else:
                # Créer un profil Client pour l'utilisateur
                ClientProfile.objects.create(user=user)
                
            messages.success(request, 'Inscription réussie! Bienvenue sur notre plateforme.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('home')

@login_required
def profile(request):
    user = request.user
    
    # Vérifiez si le profil existe, sinon créez-le
    if user.user_type == User.FREELANCER:
        if not hasattr(user, 'freelancer_profile'):
            FreelancerProfile.objects.create(user=user)  # Créez le profil Freelancer s'il n'existe pas
    else:
        if not hasattr(user, 'client_profile'):
            ClientProfile.objects.create(user=user)  # Créez le profil Client s'il n'existe pas

    # Traitement du formulaire de mise à jour
    if request.method == 'POST':
        user_form = ProfileUpdateForm(request.POST, instance=user)
        
        if user.user_type == User.FREELANCER:
            profile_form = FreelancerProfileForm(request.POST, instance=user.freelancer_profile)
        else:
            profile_form = ClientProfileForm(request.POST, instance=user.client_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Votre profil a été mis à jour!')
            return redirect('profile')
    else:
        user_form = ProfileUpdateForm(instance=user)
        
        if user.user_type == User.FREELANCER:
            profile_form = FreelancerProfileForm(instance=user.freelancer_profile)
        else:
            profile_form = ClientProfileForm(instance=user.client_profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def dashboard(request):
    user = request.user
    
    if user.user_type == User.FREELANCER:
        projects = user.bids.all().select_related('project')
        context = {
            'active_projects': projects.filter(status='AC'),
            'completed_projects': projects.filter(status='CO'),
        }
    else:
        projects = user.projects.all()
        context = {
            'active_projects': projects.filter(status='IP'),
            'completed_projects': projects.filter(status='CO'),
            'open_projects': projects.filter(status='OP'),
        }
    
    return render(request, 'accounts/dashboard.html', context)
