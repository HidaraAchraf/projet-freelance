from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Bid
from projects.models import Project
from .forms import BidForm, BidStatusForm
from messaging.models import Conversation, Message

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Bid
from projects.models import Project

@login_required
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # Vérifier que l'utilisateur est le freelance de l'offre acceptée
    accepted_bid = project.bids.filter(status=Bid.ACCEPTED).first()
    if not accepted_bid or accepted_bid.freelancer != request.user:
        messages.error(request, "Vous n'avez pas la permission de compléter ce projet.")
        return redirect('projects:detail', pk=project_id)

    if project.status != Project.IN_PROGRESS:
        messages.warning(request, "Ce projet ne peut pas être complété.")
        return redirect('projects:detail', pk=project_id)

    project.mark_as_completed()
    messages.success(request, "Projet marqué comme terminé !")
    return redirect('projects:detail', pk=project_id)

@login_required
def create_bid(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # Vérifier que l'utilisateur est un freelance
    if request.user.user_type != 'FL':
        messages.error(request, "Seuls les freelances peuvent soumettre des offres.")
        return redirect('projects:detail', pk=project_id)

    # Vérifier que le freelance n'a pas déjà soumis une offre
    if Bid.objects.filter(project=project, freelancer=request.user).exists():
        messages.warning(request, "Vous avez déjà soumis une offre pour ce projet.")
        return redirect('projects:detail', pk=project_id)

    if request.method == 'POST':
        form = BidForm(request.POST, project=project, freelancer=request.user)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.project = project
            bid.freelancer = request.user
            bid.save()

            # Créer une conversation liée à ce projet si elle n'existe pas
            conversation, created = Conversation.objects.get_or_create(project=project)
            conversation.participants.add(request.user, project.client)

            messages.success(request, "Votre offre a été soumise avec succès!")
            return redirect('projects:detail', pk=project_id)
    else:
        form = BidForm(project=project, freelancer=request.user)

    context = {
        'form': form,
        'project': project,
    }
    return render(request, 'bids/create.html', context)

@login_required
def withdraw_bid(request, bid_id):
    # Récupérer l'offre
    bid = get_object_or_404(Bid, pk=bid_id)

    # Vérifier si l'utilisateur est le freelance ayant soumis l'offre
    if request.user != bid.freelancer:
        messages.error(request, "Vous n'avez pas la permission de retirer cette offre.")
        return redirect('projects:detail', pk=bid.project.id)

    # Retirer l'offre
    bid.delete()
    messages.success(request, "Votre offre a été retirée avec succès.")

    return redirect('projects:detail', pk=bid.project.id)

@login_required
def edit_bid(request, bid_id):
    bid = get_object_or_404(Bid, pk=bid_id)

    # Vérifier les permissions
    if request.user != bid.freelancer:
        messages.error(request, "Vous n'avez pas la permission de modifier cette offre.")
        return redirect('projects:detail', pk=bid.project.id)

    if not bid.can_be_modified_by(request.user):
        messages.error(request, "Cette offre ne peut plus être modifiée.")
        return redirect('projects:detail', pk=bid.project.id)

    if request.method == 'POST':
        form = BidForm(request.POST, instance=bid, project=bid.project, freelancer=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre offre a été mise à jour avec succès!")
            return redirect('projects:detail', pk=bid.project.id)
    else:
        form = BidForm(instance=bid, project=bid.project, freelancer=request.user)

    context = {
        'form': form,
        'bid': bid,
        'project': bid.project,
    }
    return render(request, 'bids/edit.html', context)

@login_required
def manage_bid(request, bid_id):
    bid = get_object_or_404(Bid, pk=bid_id)

    # Vérifier que l'utilisateur est le client du projet
    if request.user != bid.project.client:
        messages.error(request, "Vous n'avez pas la permission de gérer cette offre.")
        return redirect('projects:detail', pk=bid.project.id)

    if not bid.can_be_accepted():
        messages.error(request, "Cette offre ne peut plus être modifiée.")
        return redirect('projects:detail', pk=bid.project.id)

    if request.method == 'POST':
        form = BidStatusForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            message_content = form.cleaned_data['message']

            if action == 'accept':
                # Rejeter toutes les autres offres pour ce projet
                Bid.objects.filter(
                    project=bid.project,
                    status=Bid.PENDING
                ).exclude(
                    id=bid.id
                ).update(status=Bid.REJECTED)

                bid.accept()
                messages.success(request, "L'offre a été acceptée avec succès!")

                # Créer un message de notification
                conversation = Conversation.objects.filter(
                    participants=bid.freelancer,
                    project=bid.project
                ).first()

                if conversation and message_content:
                    Message.objects.create(
                        conversation=conversation,
                        sender=request.user,
                        content=f"Votre offre a été acceptée!\n\n{message_content}"
                    )

                return redirect('projects:detail', pk=bid.project.id)


            elif action == 'reject':
                bid.reject()
                messages.success(request, "L'offre a été rejetée.")

                # Créer un message de notification
                conversation = Conversation.objects.filter(
                    participants=bid.freelancer,
                    project=bid.project
                ).first()

                if conversation and message_content:
                    Message.objects.create(
                        conversation=conversation,
                        sender=request.user,
                        content=f"Votre offre a été rejetée.\n\n{message_content}"
                    )

                return redirect('projects:detail', pk=bid.project.id)
    else:
        form = BidStatusForm()

    context = {
        'form': form,
        'bid': bid,
        'project': bid.project,
    }
    return render(request, 'bids/manage.html', context)

@login_required
def bid_list(request):
    if request.user.user_type == 'FL':
        bids = Bid.objects.filter(freelancer=request.user).order_by('-created_at')
    else:
        bids = Bid.objects.filter(project__client=request.user).order_by('-created_at')

    context = {
        'bids': bids,
    }
    return render(request, 'bids/list.html', context)

@login_required
def bid_detail(request, bid_id):
    bid = get_object_or_404(Bid, pk=bid_id)

    if not bid.can_be_viewed_by(request.user):
        messages.error(request, "Vous n'avez pas accès à cette offre.")
        return redirect('dashboard')

    context = {
        'bid': bid,
        'project': bid.project,
        'can_manage': request.user == bid.project.client and bid.can_be_accepted(),
        'can_edit': bid.can_be_modified_by(request.user),
    }
    return render(request, 'bids/detail.html', context)
