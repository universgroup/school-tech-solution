# Create your views here.
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ConnexionForm, CreationUtilisateurForm, ModificationUtilisateurForm

Utilisateur = get_user_model()


class ConnexionView(LoginView):
    authentication_form = ConnexionForm
    redirect_authenticated_user = True


class DeconnexionView(LogoutView):
    next_page = 'connexion'


def _est_directeur_general(user):
    return user.is_authenticated and user.est_directeur_general()


@login_required
@user_passes_test(_est_directeur_general)
def liste_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all().order_by('last_name')
    return render(request, 'gUsers/liste_utilisateurs.html', {'utilisateurs': utilisateurs})


@login_required
@user_passes_test(_est_directeur_general)
def creer_utilisateur(request):
    if request.method == 'POST':
        form = CreationUtilisateurForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur créé avec succès.")
            return redirect('liste_utilisateurs')
    else:
        form = CreationUtilisateurForm()
    return render(request, 'gUsers/creer_utilisateur.html', {'form': form})


@login_required
@user_passes_test(_est_directeur_general)
def modifier_utilisateur(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    if request.method == 'POST':
        form = ModificationUtilisateurForm(request.POST, request.FILES, instance=utilisateur)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur modifié avec succès.")
            return redirect('liste_utilisateurs')
    else:
        form = ModificationUtilisateurForm(instance=utilisateur)
    return render(request, 'gUsers/modifier_utilisateur.html', {'form': form, 'utilisateur': utilisateur})


@login_required
def mon_profil(request):
    if request.method == 'POST':
        form = ModificationUtilisateurForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour.")
            return redirect('mon_profil')
    else:
        form = ModificationUtilisateurForm(instance=request.user)
    return render(request, 'gUsers/mon_profil.html', {'form': form})

@login_required
def home(request):

    return render(request,'global/dashboard.html')