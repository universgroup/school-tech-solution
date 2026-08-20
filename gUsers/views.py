# Create your views here.
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ConnexionForm, CreationUtilisateurForm
from django.core.paginator import Paginator
from .models import NIVEAU_ACCES_CHOICES

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
def listeutilisateurs(request):
    use = Utilisateur.objects.all().order_by('id')

    pagineuser = Paginator(use, 10)
    numpageuser = request.GET.get('page')
    use = pagineuser.get_page(numpageuser)

    return render(request, 'gUsers/liste_utilisateurs.html', {'utilisateurs': use})


@login_required
@user_passes_test(_est_directeur_general)
def creerutilisateur(request):
    if request.method == 'POST':
        form = CreationUtilisateurForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Compte utilisateur créé avec succès.")
            form = CreationUtilisateurForm()
        else:
            messages.error(request, 'Vos mots de passe ne sont pas conformes. Veuillez reprendre à nouveau.')
    else:
        form = CreationUtilisateurForm()
    return render(request, 'gUsers/creer_utilisateur.html', {'form': form})


@login_required
@user_passes_test(_est_directeur_general)
def editerutilisateur(request, iduser):
    use = Utilisateur.objects.get(id=iduser)
    return render(request,'gUsers/modifier_utilisateur.html',dict(user=use, niveau_acces=NIVEAU_ACCES_CHOICES))



@login_required
def affichermonprofil(request, iduser):
    use = Utilisateur.objects.get(id=iduser)   
    return render(request, 'gUsers/mon_profil.html',dict(user=use))



@login_required
@user_passes_test(_est_directeur_general)
def modifierutilisateur(request, pk):
    if request.method == 'POST':
            use = Utilisateur.objects.get(id=pk)
            use.username = request.POST['username']
            use.first_name = request.POST['first_name']
            use.last_name = request.POST['last_name']
            use.email = request.POST['email_user']
            use.niveau_acces = request.POST['niveau_acces']

            if request.FILES.get('new_photo_profil'):
                use.photo_profil = request.FILES.get('new_photo_profil')

            if request.POST.get('passwrd'):
                use.password = request.POST['passwrd']
            use.save()
            return redirect('liste_utilisateurs')
    else:
        return redirect('../liste_utilisateurs/')


@login_required
@user_passes_test(_est_directeur_general)
def supprimerutilisateur(request, iduser):
    use = Utilisateur.objects.get(id=iduser)
    use.delete()
    return redirect('../liste_utilisateurs/')
    


@login_required
def home(request):

    return render(request,'global/dashboard.html')