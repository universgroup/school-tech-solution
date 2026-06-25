from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator  # Utilisé dans la gestion des paginations des différentes listes de données
from django.utils.datastructures import MultiValueDictKeyError
from .models import *
from .forms import *
from django.db.models import Q


# Gestion des Cycles Scolaires
def enregistrercycle(request):
    if request.method == 'POST':
        formcycle = FormCycle(request.POST)
        if formcycle.is_valid():
            cy = request.POST.get('cycle')

            if cy == 'Selectionnez':
                messages.error(request, 'Nom de cycle invalide. Veuillez sélectionner un cycle dans la liste')
            else:
                existecycle = CycleScolaire.objects.filter(cycle__exact=cy)

                if existecycle.exists():
                    messages.error(request, 'Cycle déjà enregistré')
                else:
                    formcycle.save()
                    formcycle = FormCycle()
                    messages.success(request, 'Cycle ajouté avec succès')
        else:
            messages.warning(request,
                             'Les données saisies sont invalides, veuillez respecter les critères de validation')
    else:
        formcycle = FormCycle()

    return render(request, 'gAdministration/enregistrer_cycle.html', dict(form=formcycle))


def listecyclescolaire(request):
    cycles = CycleScolaire.objects.all().order_by('id')
    paginecycle = Paginator(cycles, 10)
    numpagecycle = request.GET.get('page')
    cycles = paginecycle.get_page(numpagecycle)
    return render(request, 'gAdministration/liste_cycle.html', dict(cycles=cycles))


def detailscyclescolaire(request, pk_cycle):
    cy = CycleScolaire.objects.get(id=pk_cycle)
    return render(request, 'gAdministration/afficher_details_cyclescolaire.html', dict(cycle=cy))


def editercyclescolaire(request, pk):
    cy = CycleScolaire.objects.get(id=pk)
    return render(request, 'gAdministration/modifier_cyclescolaire.html', dict(cycle=cy))


def modifiercyclescolaire(request, idcycle):
    if request.method == 'POST':
        cy = CycleScolaire.objects.get(id=idcycle)
        cy.cycle = request.POST.get('nom_cycle')
        cy.save()
        return redirect('../listecycle/')
    else:
        return redirect('../listecycle/')


def supprimercyclescolaire(request, idc):
    cy = CycleScolaire.objects.get(id=idc)
    cy.delete()
    messages.success(request, 'Cycle supprimé avec succès')
    return redirect('../listecycle/')


# Gestion des Classes
def enregistrerclasse(request):
    if request.method == 'POST':
        formclasse = FormClasse(request.POST)  # Ici je vais recuperer les données saisies
        if formclasse.is_valid():  # Ici je verifie si elles sont valides
            nc = request.POST['nom_classe']
            c = request.POST['idcycle']  # Je recupère l'ID du cycle selectionné
            cy = CycleScolaire.objects.get(
                id=c)  # Je fais une requete sur la table CycleScolaire pour recuperer l'ID Cycle concerné
            fi = Decimal(request.POST['frais_inscription'])
            fr = Decimal(request.POST['frais_reinscription'])
            tr1 = Decimal(request.POST['tranche1'])
            tr2 = Decimal(request.POST['tranche2'])
            fs = Decimal(tr1 + tr2) # La scolarité est la somme des deux tranches

            existeclasse = Classe.objects.filter(
                nom_classe__exact=nc)  # Ici je cherche à gerer les doublons dans la saisie des noms de classe
            if existeclasse.exists():
                messages.error(request, 'Cette classe existe déjà')
            else:
                cls = Classe(nom_classe=nc, idcycle=cy, frais_inscription=fi, frais_reinscription=fr, tranche1=tr1, tranche2=tr2,
                             frais_scolarite=fs)
                cls.save()
                formclasse = FormClasse()  # je vide ensuite le formulaire
                messages.success(request, 'Classe enregistrée avec succès')
        else:
            messages.warning(request,
                             'Les données saisies sont invalides, veuillez respecter les critères de validation')
    else:
        formclasse = FormClasse()  # Permet de creer une nouvelle instance du formulaire
    return render(request, 'gAdministration/enregistrer_classe.html', {'form': formclasse})


#
def listeclasse(request):
    clas = Classe.objects.all().order_by(
        'idcycle')  # Permet d'afficher la liste des Classes par ordre croissant des Cycles
    pagineclas = Paginator(clas, 10)
    num_pageclas = request.GET.get('page')
    clas = pagineclas.get_page(num_pageclas)
    return render(request, 'gAdministration/liste_classe.html', {'clas': clas})


# # Cette fonction permet de recuperer les données de l'objet selectionné dans le formulaire Liste Classe
def editerclasse(request, idclas):
    clas = Classe.objects.get(id=idclas)
    return render(request, 'gAdministration/modifier_classe.html', {'clas': clas})


def detailsclasse(request, pk):
    clas = Classe.objects.get(id=pk)
    return render(request, 'gAdministration/afficher_details_classe.html', dict(clas=clas))


# # Cette autre fonction me permet de valider la mis à jour d'une Classe
def modifierclasse(request, idclasse):
    if request.method == 'POST':
        clas = Classe.objects.get(id=idclasse)
        clas.nom_classe = request.POST['nom_classe']
        clas.frais_inscription = Decimal(request.POST['frais_inscription'])
        clas.frais_reinscription = Decimal(request.POST['frais_reinscription'])
        clas.tranche1 = Decimal(request.POST['tranche1'])
        clas.tranche2 = Decimal(request.POST['tranche2'])
        clas.frais_scolarite = Decimal(clas.tranche1 + clas.tranche2)
        clas.save()
        return redirect('../listeclasse/')
    else:
        return redirect('../listeclasse/')


def supprimerclasse(request, idclasse):
    clas = Classe.objects.get(id=idclasse)
    clas.delete()
    messages.success(request, 'Classe supprimée avec succès')
    return redirect('../listeclasse/')


# Gestion de l'année scolaire
def ajouteranneescolaire(request):
    if request.method == 'POST':
        formannee = FormAnneeScolaire(request.POST)
        if formannee.is_valid():
            ans = request.POST.get('descript_annee')
            if AnneeScolaire.objects.filter(descript_annee__exact=ans).exists():
                messages.error(request, 'Cette année scolaire est déjà ajoutée')
            else:
                formannee.save()
                formannee = FormAnneeScolaire()
                messages.success(request, 'Année scolaire ajoutée avec succès')
        else:
            messages.warning(request,
                             'Les données saisies sont invalides, veuillez respecter les critères de validation')
    else:
        formannee = FormAnneeScolaire()  # J'ai instancié le formulaire au niveau global de la fonction pourque cet objet "formannee" soit reconnue dans celle-ci

    context = {'form': formannee}
    return render(request, 'gAdministration/enregistrer_anneescolaire.html', context)


def listeanneescolaire(request):
    ansc = AnneeScolaire.objects.all().order_by('descript_annee')
    pagineans = Paginator(ansc, 10)
    numpageans = request.GET.get('page')
    ansc = pagineans.get_page(numpageans)
    return render(request, 'gAdministration/liste_annee_scolaire.html', dict(ansc=ansc))


def editeranneescolaire(request, idanne):
    ans = AnneeScolaire.objects.get(id=idanne)
    context = {'ansc': ans}
    return render(request, 'gAdministration/modifier_anneescolaire.html', context)


def detailsanneescolaire(request, idans):
    ansc = AnneeScolaire.objects.get(id=idans)
    return render(request, 'gAdministration/afficher_details_anneescolaire.html', dict(ansc=ansc))


def modifieranneescolaire(request, idanne):
    if request.method == 'POST':
        ans = AnneeScolaire.objects.get(id=idanne)
        ans.descript_annee = request.POST['descript_annee']
        ans.save()
        return redirect('../listeanneescolaire/')
    else:
        return redirect('../listeanneescolaire/')


def supprimeranneescolaire(request, pk):
    ans = AnneeScolaire.objects.get(id=pk)
    ans.delete()
    messages.success(request, 'Année scolaire supprimée')
    return redirect('../listeanneescolaire/')


# Gestion des informations de l'ecole
def enregistrerinfosecole(request):
    if request.method == 'POST':
        fecole = FormEcole(request.POST)
        if fecole.is_valid():
            ne = request.POST.get('nom_ecole')
            vil = request.POST.get('ville_ecole')
            agre = request.POST.get('agrement_ecole')

            if Ecole.objects.filter(Q(nom_ecole__exact=ne), Q(ville_ecole__exact=vil),
                                    Q(agrement_ecole__exact=agre)).exists():
                messages.error(request, 'Les infos de l\'école sont déjà enregistrées')
            else:
                ecole = Ecole()
                ecole.nom_ecole = request.POST['nom_ecole']
                ecole.ville_ecole = request.POST['ville_ecole']
                ecole.agrement_ecole = request.POST['agrement_ecole']
                ecole.prefect_commune = request.POST['prefect_commune']
                ecole.bp_ecole = request.POST['bp_ecole']
                ecole.telephone1 = request.POST['telephone1']
                ecole.telephone2 = request.POST['telephone2']
                ecole.email_ecole = request.POST['email_ecole']
                ecole.site_internet = request.POST['site_internet']
                ecole.devise_ecole = request.POST['devise_ecole']
                try:
                    ecole.logo_ecole = request.FILES.get('logo_ecole')
                    ecole.signa_dg = request.FILES.get('signa_dg')
                    ecole.signa_de = request.FILES.get('signa_de')
                except MultiValueDictKeyError:
                    pass
                ecole.dsee = request.POST['dsee']
                ecole.dg = request.POST['dg']
                ecole.coordo_primaire = request.POST['coordo_primaire']
                ecole.coordo_secondaire = request.POST['coordo_secondaire']
                ecole.comptable = request.POST['comptable']
                ecole.save()

                messages.success(request, 'Informations de l\'école validées avec succès')
                fecole = FormEcole()
        else:
            messages.warning(request,
                             'Les données saisies sont invalides, veuillez respecter les critères de validation')

    else:
        fecole = FormEcole()

    return render(request, 'gAdministration/enregistrer_infos_ecole.html', dict(form=fecole))


def listeinfosecole(request):
    infos = Ecole.objects.all()
    pagineecole = Paginator(infos, 10)
    numpageecole = request.GET.get('page')
    infos = pagineecole.get_page(numpageecole)
    return render(request, 'gAdministration/liste_infos_ecole.html', dict(ecole=infos))


def detailsinfosecole(request, idec):
    infos = Ecole.objects.get(id=idec)
    return render(request, 'gAdministration/afficher_details_ecole.html', dict(ecole=infos))


def editerinfosecole(request, pk):
    infos = Ecole.objects.get(id=pk)
    return render(request, 'gAdministration/modifier_infos_ecole.html', dict(ecole=infos))


def modifierinfosecole(request, idec):
    
    if request.method == 'POST':
        infos = Ecole.objects.get(id=idec)
        infos.nom_ecole = request.POST['nom_ecole']
        infos.ville_ecole = request.POST['ire']
        infos.prefect_commune = request.POST['dce']
        infos.dsee = request.POST['dsee']
        infos.telephone1 = request.POST['tel1']
        infos.telephone2 = request.POST['tel2']
        infos.agrement_ecole = request.POST['num_agrement']
        infos.bp_ecole = request.POST['bp']
        infos.email_ecole = request.POST['email_ecole']
        infos.site_internet = request.POST['site_web']
        infos.devise_ecole = request.POST['devise']
        infos.dg = request.POST['dg']
        infos.coordo_primaire = request.POST['coordop']
        infos.coordo_secondaire = request.POST['coordos']
        infos.comptable = request.POST['comptable']
        
        if request.FILES.get('logo_new'):
            infos.logo_ecole = request.FILES.get('logo_new')
        else:
            pass

        if request.FILES.get('signe_dg'):
            infos.signa_dg = request.FILES.get('signe_dg')
        else:
            pass

        if request.FILES.get('signe_de'):
            infos.signa_de = request.FILES.get('signe_de')
        else:
            pass

        infos.save()
        return redirect('../listeinfos/')
    else:
        return redirect('../listeinfos/')
