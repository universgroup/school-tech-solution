from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import *
from .forms import *


# Create your views here.

# Gestion des Matieres
def enregistrermatiere(request):
    if request.method == 'POST':
        formmatiere = FormMatiere(request.POST)
        if formmatiere.is_valid():
            formmatiere.save()
            formmatiere = FormMatiere()
            messages.success(request, 'Matière ajoutée avec succès')
    else:
        formmatiere = FormMatiere()
    return render(request, 'gCours/enregistrer_matiere.html', {'form': formmatiere})


def listematiere(request):
    mat = Matiere.objects.all().order_by('nom_matiere')
    paginemat = Paginator(mat, 10)  # Permet de définir une pagination sur 10 lignes/enregistrements
    num_pagemat = request.GET.get('page')  # Permet de recuperer le numéro de page selectionné
    mat = paginemat.get_page(num_pagemat)  # J'affiche la page correspondant au numéro selectionné
    context = {'mat': mat}
    return render(request, 'gCours/liste_matiere.html', context)


def editermatiere(request, idmat):
    mat = Matiere.objects.get(id=idmat)
    context = {'mat': mat}
    return render(request, 'gCours/modifier_matiere.html', context)


def detailsmatiere(request, codemat):
    mat = Matiere.objects.get(id=codemat)
    return render(request, 'gCours/afficher_details_matiere.html', dict(mat=mat))


def modifiermatiere(request, idmat):
    if request.method == 'POST':
        mat = Matiere.objects.get(id=idmat)
        mat.nom_matiere = request.POST['nom_matiere']
        mat.coeff = request.POST['coeff']
        mat.save()
        return redirect('/listematiere/')
    else:
        return redirect('/listematiere/')


def supprimermatiere(request, idmat):
    mat = Matiere.objects.get(id=idmat)
    mat.delete()
    messages.success(request, 'Matière supprimée avec succès')
    return redirect('/listematiere/')
