from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project
from .forms import ProjectForm
from bids.models import Bid
from accounts.models import User

@login_required
def project_list(request):
    projects = Project.objects.filter(status=Project.OPEN).order_by('-created_at')
    
    # Filtrage pour les freelancers (par compétences)
    if request.user.user_type == User.FREELANCER:
        skills = request.user.freelancer_profile.skills.split(',')
        projects = projects.filter(skills_required__in=skills)
    
    return render(request, 'projects/list.html', {'projects': projects})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user_bid = None
    
    if request.user.user_type == User.FREELANCER:
        user_bid = Bid.objects.filter(project=project, freelancer=request.user).first()
    
    bids = project.bids.all().order_by('amount')
    
    context = {
        'project': project,
        'bids': bids,
        'user_bid': user_bid,
        'can_edit': request.user == project.client,
    }
    
    return render(request, 'projects/detail.html', context)

@login_required
def create_project(request):
    if request.user.user_type != User.CLIENT:
        messages.warning(request, 'Seuls les clients peuvent créer des projets.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.client = request.user
            project.save()
            request.user.client_profile.posted_projects += 1
            request.user.client_profile.save()
            messages.success(request, 'Projet créé avec succès!')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'projects/create.html', {'form': form})

@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.user != project.client:
        messages.warning(request, "Vous n'avez pas la permission de modifier ce projet.")
        return redirect('projects:detail', pk=pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Projet mis à jour avec succès!')
            return redirect('projects:detail', pk=pk)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'projects/edit.html', {'form': form, 'project': project})

@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.user != project.client:
        messages.warning(request, "Vous n'avez pas la permission de supprimer ce projet.")
        return redirect('projects:detail', pk=pk)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Projet supprimé avec succès!')
        return redirect('projects:list')
    
    return render(request, 'projects/confirm_delete.html', {'project': project})
@login_required
def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Vérifier que le projet est en cours
    if project.status != Project.IN_PROGRESS:
        messages.warning(request, "Ce projet ne peut pas être complété.")
        return redirect('projects:detail', pk=project.id)

    # Vérifier que l'utilisateur est le freelance de l'offre acceptée
    accepted_bid = project.bids.filter(status=Bid.ACCEPTED).first()
    if not accepted_bid or accepted_bid.freelancer != request.user:
        messages.error(request, "Vous n'avez pas la permission de compléter ce projet.")
        return redirect('projects:detail', pk=project.id)

    # Marquer comme terminé
    project.mark_as_completed()
    messages.success(request, "Projet marqué comme terminé !")
    return redirect('projects:detail', pk=project.id)