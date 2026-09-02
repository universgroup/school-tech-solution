from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseRedirect, FileResponse

from .models import *
from .forms import *
from decimal import Decimal
from django.db.models import Sum, Q
from gAdministration.models import AnneeScolaire, Historique, CycleScolaire, Ecole
from gEleve.models import Inscription

#from django.utils.datastructures import MultiValueDictKeyError
from datetime import datetime, date
import re # Librairie contenant les fonctions de gestion des regex
import socket
from smtplib import SMTPException

from reportlab.pdfgen import canvas
from reportlab.lib import colors  # Contient les méthodes/fonctions de gestion des couleurs
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, NextPageTemplate,
    Table, TableStyle, Paragraph, Spacer)
from reportlab.platypus import Table as RLTable  # évite le conflit de nom avec votre "Table" du tableau principal
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT # TA_CENTER, 

from PIL import Image

from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings
import io  # Librairie contenant les methodes utilisant les péripheriques d'entrées/sorties
from gUsers.decorators import action_requise
from django.contrib.auth.decorators import login_required

# Create your views here.

# Cette fonction me permet de recuperer le dernier solde caisse

def affichersoldecaisse():
    try:
        cais = Caisse.objects.latest('id')  # Ici je tente de recuperer le dernier solde caisse
    except Caisse.DoesNotExist: \
            cais = None
    if cais:
        solde = cais.solde_actuel
    else:
        solde = 0
    return solde


# Gestion de la Caisse Scolarité
@action_requise('compta_ajouter')
def enregistrer_recette(request):
    if request.method == 'POST':
        formrecette = FormCaisseScolarite(request.POST)
        if formrecette.is_valid():
            an = request.POST['anscolaire']
            ans = AnneeScolaire.objects.get(id=an)
            cai = Caisse()
            cai.type_operation = request.POST['type_operation']
            cai.libelle_operation = request.POST['libelle_operation']
            cai.categ_depense = request.POST['categ_depense']
            cai.anscolaire = ans
            cai.observ = request.POST['observ']
            mont = request.POST['montant_encaisse']
            cai.montant_encaisse = Decimal(mont)
            cai.solde_actuel = Decimal(affichersoldecaisse()) + Decimal(mont)
            cai.date_operation = request.POST['date_operation']
            cai.save()
            formrecette = FormCaisseScolarite()
            messages.success(request, 'Opération validée avec succès')

            # Ici je vais enregistrer l'evenement dans la table Historique
            his = Historique()
            his.nature_operation = TYPE_OPERATION_CAISSE_CHOICES[1][1]
            his.detail_operation = 'Entrée en caisse d\'une valeur de : {}, pour {}'.format(
                mont, cai.libelle_operation)
            his.user_login = 'contact@universtechg'
            his.save()
        else:
            messages.warning(request, 'Vous avez saisi des données invalides!')

    else:
        formrecette = FormCaisseScolarite()

    return render(request, 'gComptabilite/enregistrer_caisse_scolarite.html', dict(form=formrecette))

@action_requise('menu_comptabilite')
def listerecette(request):
      
    mois_courant = datetime.strftime(datetime.now(),'%m') # Je recupere le numero du mois en cours en vue de filtrer les operations conformement a cela
    mactu = datetime.strftime(datetime.now(),'%B') # Le nom du mois en Toute lettre (Mars ici)
    
    cais = Caisse.objects.filter(Q(type_operation=TYPE_OPERATION_CAISSE_CHOICES[1][1]),
                                 Q(date_operation__month=mois_courant)).order_by(
        '-date_operation','id')  # Affiche la situation de la caisse des recettes par ordre décroissant de la date et ordre croissant de l'id
    # d'opération
    t_entree = Caisse.objects.filter(Q(type_operation=TYPE_OPERATION_CAISSE_CHOICES[1][1]),
                                     Q(date_operation__month=mois_courant)).aggregate(
        entree=Sum('montant_encaisse'))
    t_sortie = Caisse.objects.filter(Q(type_operation=TYPE_OPERATION_CAISSE_CHOICES[2][1]),
                                     Q(date_operation__month=mois_courant)).aggregate(
        sortie=Sum('montant_encaisse'))
    solde_dispo = Decimal(affichersoldecaisse())

    total_entree = 0
    total_sortie = 0

    if t_entree['entree'] is not None:
        total_entree = t_entree[
            'entree']  # Permet de recuperer le montant total des recettes du dictionnaire obtenu après la requête de
    # filtre ci-dessus; 'entree' est un alias de la colonne Sum('montant_encaisse')
    else:
        total_entree = 0

    if t_sortie['sortie'] is not None:
        total_sortie = t_sortie[
            'sortie']  # # Permet de recuperer le montant total des dépenses du dictionnaire obtenu après la requête de
    # filtre ci-dessus; 'sortie' est un alias de la colonne Sum('montant_encaisse')
    else:
        total_sortie = 0

    annee = AnneeScolaire.objects.all().order_by(
        'id')  # Permet de recuperer la liste générale des années scolaires en vue de charger la dropdown liste

    paginecais = Paginator(cais, 10)
    numpagecais = request.GET.get('page')
    cais = paginecais.get_page(numpagecais)
    
    return render(request, 'gComptabilite/liste_recettes.html',
                  dict(cais=cais, total_entree=total_entree, total_sortie=total_sortie,
                       solde_dispo=solde_dispo, annee=annee,mois_actuel=mactu))

@action_requise('compta_modifier')
def detailscaisserecette(request, idcais):
    cais = Caisse.objects.get(id=idcais)
    return render(request, 'gComptabilite/afficher_details_caisse_scolarite.html', dict(cais=cais))

@action_requise('compta_modifier')
def editercaisserecette(request, idcais):
    cais = Caisse.objects.get(id=idcais)
    return render(request, 'gComptabilite/modifier_caisse_scolarite.html', dict(cais=cais))

@action_requise('compta_modifier')
def modifiercaisserecette(request, idcais):
    if request.method == 'POST':
        cais = Caisse.objects.get(id=idcais)
        cais.libelle_operation = request.POST['libelle_operation']
        cais.observ = request.POST['observ']
        cais.date_operation = request.POST['date_operation']
        cais.save()
        return redirect('../listerecette/')
    else:
        return redirect('../listerecette/')

@action_requise('compta_supprimer')
def supprimercaisserecette(request, pk):
    cais = Caisse.objects.get(id=pk)
    cais.delete()
    messages.success(request, 'Ligne de recette supprimée avec succès')
    return redirect('../listerecette/')


t_entree = {}
t_sortie = {}
recette = {}
solde_dispo = 0
debut = None
fin = None

@action_requise('menu_comptabilite')
def recherchersituationrecette(request):
    
    ans = request.GET.get('nom_annee')
    ddebut = request.GET.get('ddebut')
    dfin = request.GET.get('dfin')
    
    global t_entree
    global t_sortie
    global recette
    global solde_dispo
    global debut, fin
    
    total_entree = 0
    total_sortie = 0
    recette = Caisse.objects.none() # Initialisation de base pour eviter le bug lié au keyerror slice(0,0,None) lors du filtre par annee scolaire
    
           
    if (ans !='' and ans is not None) and (ddebut =='' and ddebut is None) and (dfin =='' and dfin is None):
        
        recette = Caisse.objects.filter(Q(anscolaire__exact=ans),
                                    Q(type_operation__exact=TYPE_OPERATION_CAISSE_CHOICES[1][1])).all().order_by(
        '-date_operation','id')
        t_entree = Caisse.objects.filter(Q(type_operation=TYPE_OPERATION_CAISSE_CHOICES[1][1]),
                                     Q(anscolaire__exact=ans)).aggregate(
        entree=Sum('montant_encaisse'))
        t_sortie = Caisse.objects.filter(Q(type_operation=TYPE_OPERATION_CAISSE_CHOICES[2][1]),
                                     Q(anscolaire__exact=ans)).aggregate(
        sortie=Sum('montant_encaisse'))
        solde_dispo = Decimal(affichersoldecaisse())
        
        
        if t_entree['entree'] is not None:
            total_entree = t_entree[
                'entree']  # Permet de recuperer le montant total des recettes du dictionnaire obtenu après la requête de
        # filtre ci-dessus; 'entree' est un alias de la colonne Sum('montant_encaisse')
        else:
            total_entree = 0

        if t_sortie['sortie'] is not None:
            total_sortie = t_sortie[
                'sortie']  # # Permet de recuperer le montant total des dépenses du dictionnaire obtenu après la requête de
        # filtre ci-dessus; 'sortie' est un alias de la colonne Sum('montant_encaisse')
        else:
            total_sortie = 0
        
        
    elif (ans !='' and ans is not None) and (ddebut !='' and ddebut is not None) and (dfin !='' and dfin is not None):
                
        debut = datetime.strptime(ddebut,'%Y-%m-%d')
        fin = datetime.strptime(dfin,'%Y-%m-%d') 
               
        recette = Caisse.objects.filter(Q(anscolaire__exact=ans),
                                    Q(type_operation__exact=TYPE_OPERATION_CAISSE_CHOICES[1][1]),Q(date_operation__range=(debut,fin))).all().order_by(
        '-date_operation','id')
        t_entree = Caisse.objects.filter(Q(type_operation=TYPE_OPERATION_CAISSE_CHOICES[1][1]),
                                     Q(anscolaire__exact=ans),Q(date_operation__range=(debut,fin))).aggregate(
        entree=Sum('montant_encaisse'))
        t_sortie = Caisse.objects.filter(Q(type_operation=TYPE_OPERATION_CAISSE_CHOICES[2][1]),
                                     Q(anscolaire__exact=ans),Q(date_operation__range=(debut,fin))).aggregate(
        sortie=Sum('montant_encaisse'))
        solde_dispo = Decimal(affichersoldecaisse())
        
        if t_entree['entree'] is not None:
            total_entree = t_entree[
                'entree']  # Permet de recuperer le montant total des recettes du dictionnaire obtenu après la requête de
        # filtre ci-dessus; 'entree' est un alias de la colonne Sum('montant_encaisse')
        else:
            total_entree = 0

        if t_sortie['sortie'] is not None:
            total_sortie = t_sortie[
                'sortie']  # # Permet de recuperer le montant total des dépenses du dictionnaire obtenu après la requête de
        # filtre ci-dessus; 'sortie' est un alias de la colonne Sum('montant_encaisse')
        else:
            total_sortie = 0       

    annee = AnneeScolaire.objects.all().order_by(
            'id')  # Permet de recuperer la liste générale des années scolaires en vue de charger la dropdown liste


    paginecais = Paginator(recette, 10)
    numpagecais = request.GET.get('page')
    recette = paginecais.get_page(numpagecais)
    return render(request, 'gComptabilite/liste_recettes.html',
                  dict(recette=recette, total_entree=total_entree, total_sortie=total_sortie, solde_dispo=solde_dispo, ddebut=debut, dfin=fin, annee=annee))

@action_requise('compta_ajouter')
def enregistrerdepense(request):
    if request.method == 'POST':
        fdepense = FormDepense(request.POST)
        if fdepense.is_valid():
            ans = request.POST.get('anscolaire')
            soldec = affichersoldecaisse()
            idane = AnneeScolaire.objects.get(id=ans)
            cais = Caisse()
            cais.anscolaire = idane
            cais.type_operation = request.POST['type_operation']
            cais.libelle_operation = request.POST['libelle_operation']
            cais.categ_depense = request.POST['categ_depense']
            cais.qte = request.POST['qte']
            cais.pua = request.POST['pua']
            cais.provient = request.POST['provient']
            cais.destine = request.POST['destine']
            cais.montant_encaisse = Decimal(cais.qte) * Decimal(cais.pua)
            cais.observ = request.POST['observ']
            cais.date_operation = request.POST['date_operation']

            if request.FILES.get('piece_jointe'):
                cais.piece_jointe = request.FILES.get('piece_jointe')

            if soldec > cais.montant_encaisse:
                cais.solde_actuel = soldec - cais.montant_encaisse
                cais.save()
                messages.success(request, 'Ligne de dépense validée avec succès. \n Montant opération : {}'.format(
                    cais.montant_encaisse))

                # Ici je vais enregistrer l'evenement dans la table Historique
                his = Historique()
                his.nature_operation = TYPE_OPERATION_CAISSE_CHOICES[2][1]
                his.detail_operation = 'Entrée en caisse d\'une valeur de : {}, pour {}'.format(
                    cais.montant_encaisse, cais.libelle_operation)
                his.user_login = 'contact@universtechg'
                his.save()

                fdepense = FormDepense()
            else:
                messages.error(request, 'Solde caisse insuffisant pour valider cette opération')
        else:
            messages.warning(request, 'Les données saisies contiennes des erreurs de validation!')
    else:
        fdepense = FormDepense()
    return render(request, 'gComptabilite/enregistrer_depense.html', dict(form=fdepense))


@action_requise('menu_comptabilite')
def listedepense(request):
  
    mois_courant = datetime.strftime(datetime.now(),'%m') # Je recupere le numero du mois en cours en vue de filtrer les operations conformement a cela
    mactu = datetime.strftime(datetime.now(),'%B') # Le nom du mois en Toute lettre (Mars ici)
    
    cais = Caisse.objects.filter(Q(type_operation=TYPE_OPERATION_CAISSE_CHOICES[2][1]),
                                 Q(date_operation__month=mois_courant)).order_by(
        '-date_operation','id')  # Affiche la situation de la caisse des recettes par ordre décroissant de la date
    # d'opération
    t_entree = Caisse.objects.filter(Q(type_operation=TYPE_OPERATION_CAISSE_CHOICES[1][1]),
                                     Q(date_operation__month=mois_courant)).aggregate(
        entree=Sum('montant_encaisse'))
    t_sortie = Caisse.objects.filter(Q(type_operation=TYPE_OPERATION_CAISSE_CHOICES[2][1]),
                                     Q(date_operation__month=mois_courant)).aggregate(
        sortie=Sum('montant_encaisse'))
                                     
    solde_dispo = Decimal(affichersoldecaisse())

    total_entree = 0
    total_sortie = 0

    if t_entree['entree'] is not None:
        total_entree = t_entree[
            'entree']  # Permet de recuperer le montant total des recettes du dictionnaire obtenu après la requête de
    # filtre ci-dessus; 'entree' est un alias de la colonne Sum('montant_encaisse')
    else:
        total_entree = 0

    if t_sortie['sortie'] is not None:
        total_sortie = t_sortie[
            'sortie']  # # Permet de recuperer le montant total des dépenses du dictionnaire obtenu après la requête de
    # filtre ci-dessus; 'sortie' est un alias de la colonne Sum('montant_encaisse')
    else:
        total_sortie = 0

    annee = AnneeScolaire.objects.all().order_by(
        'id')  # Permet de recuperer la liste générale des années scolaires en vue de charger la dropdown liste

    paginecais = Paginator(cais, 10)
    numpagecais = request.GET.get('page')
    cais = paginecais.get_page(numpagecais)
    return render(request, 'gComptabilite/liste_depenses.html',
                  dict(cais=cais, total_entree=total_entree, total_sortie=total_sortie,
                       solde_dispo=solde_dispo, annee=annee, mois_actuel=mactu))

depense = {}
debut = None
fin = None
solde_dispo = 0

@action_requise('menu_comptabilite')
def recherchersituationdepense(request):
    
    ans = request.GET.get('nom_annee')
    ddebut = request.GET.get('ddebut')
    dfin = request.GET.get('dfin')
    
    global t_entree
    global t_sortie
    global depense
    global debut, fin
    
    total_entree = 0
    total_sortie = 0
    depense = Caisse.objects.none()
    
    if (ans !='' and ans is not None) and (ddebut =='' and ddebut is None) and (dfin =='' and dfin is None):
        
        depense = Caisse.objects.filter(Q(anscolaire__exact=ans),
                                    Q(type_operation__exact=TYPE_OPERATION_CAISSE_CHOICES[2][1])).all().order_by(
        '-date_operation','id')

        t_entree = Caisse.objects.filter(Q(type_operation=TYPE_OPERATION_CAISSE_CHOICES[1][1]),
                                     Q(anscolaire__exact=ans)).aggregate(
        entree=Sum('montant_encaisse'))
        t_sortie = Caisse.objects.filter(Q(type_operation=TYPE_OPERATION_CAISSE_CHOICES[2][1]),
                                     Q(anscolaire__exact=ans)).aggregate(
        sortie=Sum('montant_encaisse'))
        solde_dispo = Decimal(affichersoldecaisse())

        if t_entree['entree'] is not None:
            total_entree = t_entree[
            'entree']  # Permet de recuperer le montant total des recettes du dictionnaire obtenu après la requête de
        # filtre ci-dessus; 'entree' est un alias de la colonne Sum('montant_encaisse')
        else:
            total_entree = 0

        if t_sortie['sortie'] is not None:
            total_sortie = t_sortie[
            'sortie']  # # Permet de recuperer le montant total des dépenses du dictionnaire obtenu après la requête de
        # filtre ci-dessus; 'sortie' est un alias de la colonne Sum('montant_encaisse')
        else:
            total_sortie = 0
            
    elif (ans !='' and ans is not None) and (ddebut !='' and ddebut is not None) and (dfin !='' and dfin is not None):
        
        debut = datetime.strptime(ddebut,'%Y-%m-%d')
        fin = datetime.strptime(dfin,'%Y-%m-%d')
        
        depense = Caisse.objects.filter(Q(anscolaire__exact=ans),
                                    Q(type_operation__exact=TYPE_OPERATION_CAISSE_CHOICES[2][1]),Q(date_operation__range=(debut,fin))).all().order_by(
        '-date_operation','id')

        t_entree = Caisse.objects.filter(Q(type_operation=TYPE_OPERATION_CAISSE_CHOICES[1][1]),
                                     Q(anscolaire__exact=ans),Q(date_operation__range=(debut,fin))).aggregate(
        entree=Sum('montant_encaisse'))
        t_sortie = Caisse.objects.filter(Q(type_operation=TYPE_OPERATION_CAISSE_CHOICES[2][1]),
                                     Q(anscolaire__exact=ans),Q(date_operation__range=(debut,fin))).aggregate(
        sortie=Sum('montant_encaisse'))
        solde_dispo = Decimal(affichersoldecaisse())

        if t_entree['entree'] is not None:
            total_entree = t_entree[
            'entree']  # Permet de recuperer le montant total des recettes du dictionnaire obtenu après la requête de
        # filtre ci-dessus; 'entree' est un alias de la colonne Sum('montant_encaisse')
        else:
            total_entree = 0

        if t_sortie['sortie'] is not None:
            total_sortie = t_sortie[
            'sortie']  # # Permet de recuperer le montant total des dépenses du dictionnaire obtenu après la requête de
        # filtre ci-dessus; 'sortie' est un alias de la colonne Sum('montant_encaisse')
        else:
            total_sortie = 0


    annee = AnneeScolaire.objects.all().order_by(
                'id')  # Permet de recuperer la liste générale des années scolaires en vue de charger la dropdown liste
            

    paginecais = Paginator(depense, 10)
    numpagecais = request.GET.get('page')
    depense = paginecais.get_page(numpagecais)

    return render(request, 'gComptabilite/liste_depenses.html',
                  dict(depense=depense, total_entree=total_entree, total_sortie=total_sortie, solde_dispo=solde_dispo, ddebut=debut, dfin=fin, annee=annee))

@action_requise('compta_modifier')
def detailsdepense(request, id):
    depense = Caisse.objects.get(id=id)
    return render(request, 'gComptabilite/afficher_details_depense.html', dict(depense=depense))

@action_requise('compta_modifier')
def editerdepense(request, id):
    depense = Caisse.objects.get(id=id)
    return render(request, 'gComptabilite/modifier_depense.html', {'depense': depense})

@action_requise('compta_modifier')
def modifierdepense(request, pk):
    if request.method == 'POST':
        depense = Caisse.objects.get(id=pk)
        depense.libelle_operation = request.POST['libelle_operation']
        depense.provient = request.POST['provient']
        depense.destine = request.POST['destine']
        depense.observ = request.POST['observ']
        depense.date_operation = request.POST['date_operation']

        if request.FILES.get('new_piece'):
            depense.piece_jointe = request.FILES.get('new_piece')
        depense.save()
        return redirect('../listedepense/')
    else:
        return redirect('../listedepense/')

@action_requise('compta_supprimer')
def supprimerdepense(request, pk):
    depense = Caisse.objects.get(id=pk)
    depense.delete()
    return redirect('../listedepense/')

# Début de la Gestion des paiements de la scolarité

# Cette fonction me permet de charger la liste des élèves inscrits dans une classe donnée aucours d'une année
# scolaire donnée
@action_requise('menu_comptabilite')
def chargerlisteelevepaiement(request):
    ane = request.GET.get('anneesco') # anneesco est la valeur renvoyée depuis la fonction JQuery dans le template paiement_scolarite.html
    clas = request.GET.get('id_classe') # id_classe est recupérée depuis la fonction JQuery
    el = Inscription.objects.select_related('annee_scolaire', 'mateleve', 'idcycle', 'idclasse').filter(
        Q(annee_scolaire=ane), Q(idclasse=clas))
    return render(request, 'gComptabilite/liste_eleve_classe_cycle_paiement.html', dict(eleve=el))


# La fonction chargerlisteclasse m'a permis de gerer l'affichage des classes selon le cycle selectionné lors de
# l'inscription associé au JQuery en Front-end
@action_requise('menu_comptabilite')
def chargerlisteclassepaiement(request):
    cy = request.GET.get('idcycle')
    clas = Classe.objects.filter(idcycle=cy).all()
    context = {'clas': clas}
    return render(request, 'gComptabilite/liste_classe_cycle_paiement.html', context)

# Cette fonction me permet de charger les infos de l'élève sélectionné lors de la reinscription à savoir le prénom, le nom et la photo
@action_requise('menu_comptabilite')
def chargerinfoeleveclasse(request):

    matricule = request.GET.get('matricule')
    
    data = {}

    try:
        el = Eleve.objects.get(matricule=matricule)
        data.update({
            'nom': el.nom,
            'prenom': el.prenom,
            'photo': str(el.photo_eleve) if el.photo_eleve else '',
            'datenaiss': el.datenaissance,
            'lieunais': el.lieu_naissance,
            'pays': el.pays_naissance,
            'pere': el.pere,
            'mere': el.mere,
            'contact_pere': el.contact_pere,
        })
    except Eleve.DoesNotExist:
        data.update({
            'nom': '', 'prenom': '', 'photo': '', 'datenaiss': '',
            'lieunais': '', 'pays': '', 'pere': '', 'mere': '', 'contact_pere': '',
        })

    try:
        etatpaie = EtatPaiementTranche.objects.get(mateleve=matricule)
        data['tranche1'] = etatpaie.premiere_tranche
        data['tranche2'] = etatpaie.deuxieme_tranche
        data['fscolarite'] = etatpaie.fscolarite
        data['reliquat'] = etatpaie.reste_a_payer

    except EtatPaiementTranche.DoesNotExist:
        data['tranche1'] = 0
        data['tranche2'] = 0
        data['fscolarite'] = 0
        data['reliquat'] = 0
    


    return JsonResponse(data)

# Fonction me permettant de convertir le montant recupéré depuis le template Paiement_scolarite
def reformater_montant(valeur):
    montant_a_reformater = re.sub(r'[\s\u00a0\u202f]','',valeur) # Supprime tous types d'espace dans le montant
    montant_a_reformater = montant_a_reformater.replace(',','.') # remplace la virgule par les points.
    return Decimal(montant_a_reformater)

erreur = None

# Fonction permettant de valider le paiement de la scolarite
@action_requise('compta_ajouter')
def validerpaiementscolarite(request):

    t1 = 0
    t2 = 0
    fannuel = 0
    mont_paye = 0
    p_tranche = 0
    d_tranche = 0
    mremise = 0
    fscol = 0
    annee = {}
    cycle = {}
    global erreur

    annee = AnneeScolaire.objects.none()
    cycle = CycleScolaire.objects.none()

    if request.method == 'POST':
        
        ane = request.POST.get('annee_scolaire')
        clas = request.POST.get('classe')
        mat = request.POST.get('matricule')
        cycl = request.POST.get('cycle')
        modepaie = request.POST.get('mode_paiement')

        nom_tranche = request.POST.get('cbo_tranche_paye')
        mont_paye = reformater_montant(request.POST.get('montant_paye')) 
        p_tranche = reformater_montant(request.POST.get('montant_premiere_tranche')) # Je recupère le montant de la première tranche affiché dans le template
        d_tranche = reformater_montant(request.POST.get('montant_deuxieme_tranche')) # Je recupère le montant de la deuxième tranche affiché dans le template
        mremise = reformater_montant(request.POST.get('montant_remise')) # Je recupère le montant de la remise saisi


        anes = AnneeScolaire.objects.get(id=ane)
        cls = Classe.objects.get(id=clas)
        matel = Eleve.objects.get(matricule=mat)
        cy = CycleScolaire.objects.get(id=cycl)

        # Je vais recuperer les frais de la première tranche et deuxième tranche ainsi que le frais de la scolarité dans la table Classe
        t1 = cls.tranche1
        t2 = cls.tranche2
        fannuel = cls.frais_scolarite

        etatpaie = EtatPaiementTranche.objects.get(mateleve=matel.matricule) # matel.matricule car matel renvoi les données du str de la classe Eleve au lieu de matricule seulement

        etatpaie.anneescolaire = anes
        etatpaie.idclasse = cls
        etatpaie.mateleve = matel
        etatpaie.idcycle = cy
        etatpaie.date_paie = request.POST['date_paiement'] 
        etatpaie.mode_paie = modepaie

        erreur = False     

                       
        if nom_tranche == DEUX_TRANCHES_CHOICES[0][0]: # Permet de verifier la première tranche
            
            if p_tranche < t1: # Je verifie que le montant de la première tranche payée est inférieur au montant de la tranche 1 défini dans la table classe                                        
                etatpaie.premiere_tranche = p_tranche + mont_paye # Le montant de la première tranche sera égal au montant initial payé + le nouveau montant payé pour cette tranche 

            else:
                messages.error(request,'La première tranche est déjà complète. Veuillez passer à la seconde tranche !!!')
                erreur = True
                
        
        elif nom_tranche == DEUX_TRANCHES_CHOICES[1][0]: # Permet de vérifier la deuxième tranche

            if p_tranche < t1: # Je verifie ici si la première tranche n'est pas bouclée alors je renvoie une alerte pour completer celle-ci
                messages.error(request,'Vous devez finaliser le paiement de la première tranche avant de passer à la suivante')
                erreur = True
            else:
                if d_tranche < t2:
                    etatpaie.deuxieme_tranche = d_tranche + mont_paye # Le montant de la deuxième tranche sera égal au montant initial payé + le nouveau montant payé pour cette tranche

                else:
                    messages.error(request,'La scolarité est déjà complète!! cet élève ne doit plus rien pour cette année scolaire')
                    erreur = True

        if not erreur: # Si aucun message d'erreur ne s'affiche, alors on enregistre le paiement
            annee = AnneeScolaire.objects.all().order_by('id') # On recharge la liste des annees a nouveau
            cycle = CycleScolaire.objects.all().order_by('id') # on recharge la liste des cycles a nouveau
            
            fscol = (etatpaie.premiere_tranche + etatpaie.deuxieme_tranche) # Permet de calculer le paiement total effectué par l'élève
            etatpaie.fscolarite = fscol

            if mremise:
                etatpaie.reste_a_payer = (fannuel - fscol)- mremise # Le reste à payer annuel est le montant annuel dû moins le total de ses paiements oté de la remise s'il existe
                etatpaie.m_rabais = mremise
            else:
                etatpaie.reste_a_payer = fannuel - fscol

            etatpaie.save()

            solde_dispo= Decimal(affichersoldecaisse())
            # Je vais enregistrer ensuite l'opération dans la table caisse
            cais = Caisse()
            cais.type_operation = TYPE_OPERATION_CAISSE_CHOICES[1][1]
            cais.libelle_operation = 'Paiement des frais de scolarité de l\'élève:  {},  {} , {} '.format(
                matel.matricule, matel.nom, matel.prenom)
            cais.montant_encaisse = Decimal(mont_paye)
            cais.anscolaire = anes
            cais.categ_depense = CATEGORIE_RECETTE_CHOICES[1][1]
            cais.solde_actuel = Decimal(solde_dispo) + Decimal(mont_paye)
            cais.date_operation = request.POST['date_paiement']
            cais.save()

            messages.success(request,'Paiement validé avec succès !!!')

            # Ici je vais enregistrer l'evenement dans la table Historique
            his = Historique()
            his.nature_operation = CATEGORIE_RECETTE_CHOICES[1][1]
            his.detail_operation = 'Paiement des frais de scolarité de l\'élève:  {},  {} , {} '.format(
                matel.matricule, matel.nom, matel.prenom)
            his.user_login = 'contact@universtechgroup.com'
            his.save()

            # Génération du reçu de paiement de la scolarité
            idetat = etatpaie.id
            return HttpResponseRedirect(reverse('recupaiementscolarite',args=(idetat,nom_tranche,str(mont_paye),)))

        else: # Si un message d'erreur s'affiche, on recharge les données de base
            annee = AnneeScolaire.objects.all().order_by('id')
            cycle = CycleScolaire.objects.all().order_by('id')
   
    else:
        annee = AnneeScolaire.objects.all().order_by('id')
        cycle = CycleScolaire.objects.all().order_by('id')    
    


    return render(request,'gComptabilite/paiement_scolarite.html',dict(ans=annee,cycles=cycle, tranche_paye=DEUX_TRANCHES_CHOICES, modepaie=MODE_PAIEMENT_CHOICES))



@action_requise('menu_comptabilite')
def recupaiementscolarite(request, idetat, nom_tranche, mont_paye):

    montant_tranche = 0
    montant_paye = 0
    reste_a_payer = 0
    
    montant_tranche_formate = None
    montant_paye_formate = None
    reste_formate = None
    tranche_name = None

    # Et là je tente de recuperer les données d'identification de l'école
    ec = Ecole.objects.count()
    if ec==0:
        messages.error(request,'Veuillez saisir les informations de l\'école')
    else:
        ecole = Ecole.objects.first()
        if ecole.logo_ecole:
            data_ecole = [ecole.nom_ecole, ecole.ville_ecole, ecole.prefect_commune, ecole.telephone1, ecole.telephone2,
                          ecole.logo_ecole.path, ecole.devise_ecole, ecole.dsee, ecole.comptable]
        else:
            data_ecole = [ecole.nom_ecole, ecole.ville_ecole, ecole.prefect_commune, ecole.telephone1, ecole.telephone2,
                          'Logo', ecole.devise_ecole, ecole.dsee, ecole.comptable]

        # Ici je tente de recuperer les données sur l'état de paiement de l'élève depuis la BD

        etatpaie = EtatPaiementTranche.objects.select_related('anneescolaire', 'mateleve', 'idclasse').get(id=idetat)
        data = [etatpaie.id, etatpaie.anneescolaire.descript_annee, etatpaie.mateleve.matricule, etatpaie.idclasse, etatpaie.mateleve.nom,
                etatpaie.mateleve.prenom,
                etatpaie.mateleve.tuteur, etatpaie.mateleve.contact_pere,etatpaie.mateleve.email_pere
                ]
        
        if nom_tranche == DEUX_TRANCHES_CHOICES[0][0]: # Si c'est la première tranche qui a été choisie, je recupère le montant de la tranche dans la table classe

            tranche_name = DEUX_TRANCHES_CHOICES[0][1] # i.e Première tranche
            montant_tranche = etatpaie.idclasse.tranche1

        elif nom_tranche == DEUX_TRANCHES_CHOICES[1][0]: # Si c'est la deuxième tranche, je recupère le montant correspondant dans la table classe

            tranche_name = DEUX_TRANCHES_CHOICES[1][0] # i.e Deuxième tranche
            montant_tranche = etatpaie.idclasse.tranche2

        montant_paye     = Decimal(mont_paye)

        # if etatpaie.m_rabais:
        #     reste_a_payer     = (montant_tranche - montant_paye)-etatpaie.m_rabais
        # else:
        reste_a_payer     = montant_tranche - montant_paye

        montant_tranche_formate   = '{:,} GNF'.format(montant_tranche)
        montant_paye_formate = '{:,} GNF'.format(montant_paye)
        reste_formate     = '{:,} GNF'.format(reste_a_payer)

        
        ch = str(data[1])  # Je recupère le nom de l'année scolaire i.e 2023-2024 par exemple
        ch = ch.split('-')  # Je découpe la chaine obtenue en deux sous chaines tenant compte du séparateur (-)
        ane = ch[1]  # Je recupère la deuxième sous chaine i.e 2024 par exemple

        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()
        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer)
        p.setTitle('Reçu Paiement Scolarité')  # Permet de définir le Titre du Document

        numrecu = data[0]  # Ici je recupère le numéro de l'inscription
        ansco = datetime.now().strftime('%y')  # Je recupère uniquement l'année de la date courante
        numero_recu = ''

        if numrecu < 10:
            numero_recu = ansco + '00' + str(numrecu)
        elif numrecu < 100:
            numero_recu = ansco + '0' + str(numrecu)
        elif numrecu < 1000:
            numero_recu = ansco + '0' + str(numrecu)
        elif numrecu < 10000:
            numero_recu = ansco + '0' + str(numrecu)
        
        def draw_recu(y_offset):
            """Dessine un reçu complet. y_offset=0 pour le haut, -420 pour le bas"""

            # ── ENTETE GAUCHE ──
            p.setFillColor(colors.black)
            p.setFont('Helvetica-Bold', 10)
            p.drawString(20, 815 + y_offset, 'MEPU-A')
            p.drawString(20, 800 + y_offset, 'IRE : ')
            p.setFont('Helvetica', 10)
            p.drawString(55, 800 + y_offset, str(data_ecole[1]))
            p.setFont('Helvetica-Bold', 10)
            p.drawString(20, 787 + y_offset, 'DCE : ')
            p.setFont('Helvetica', 10)
            p.drawString(55, 787 + y_offset, str(data_ecole[2]))
            p.setFont('Helvetica-Bold', 10)
            p.drawString(20, 772 + y_offset, 'DSEE : ')
            p.setFont('Helvetica', 10)
            p.drawString(55, 772 + y_offset, str(data_ecole[7]))
            p.setFont('Helvetica-Bold', 10)
            p.drawString(20, 757 + y_offset, 'TEL : ')
            p.setFont('Helvetica', 10)
            p.drawString(55, 757 + y_offset, str(data_ecole[3]) + ' / ' + str(data_ecole[4]))

            # ── LOGO ──
            try:
                logo = Image.open(data_ecole[5])
                logo = logo.resize((90, 60), Image.LANCZOS)
                if logo.mode in ('RGBA', 'P'):
                    logo = logo.convert('RGB')
                elif logo.mode != 'RGB':
                    logo = logo.convert('RGB')
                logo_buffer = io.BytesIO()
                logo.save(logo_buffer, format='PNG')
                logo_buffer.seek(0)
                p.drawImage(ImageReader(logo_buffer), 245, 770 + y_offset, 90, 60)
            except (FileNotFoundError, OSError):
                p.drawString(data_ecole[5], 245, 770 + y_offset)

            # ── DRAPEAU ──
            p.setFillColor('Red')
            p.rect(449, 815 + y_offset, 30, 10, stroke=False, fill=True)
            p.setFillColor('yellow')
            p.rect(479, 815 + y_offset, 30, 10, stroke=False, fill=True)
            p.setFillColor('green')
            p.rect(509, 815 + y_offset, 30, 10, stroke=False, fill=True)
            p.setFillColor(colors.black)

            # ── ENTETE DROITE ──
            p.setFont('Helvetica-Bold', 10)
            p.drawString(450, 800 + y_offset, 'République de Guinée')
            p.setFont('Helvetica-Oblique', 9)
            p.drawString(450, 785 + y_offset, 'Travail-Justice-Solidarité')

            # ── NOM ET DEVISE ECOLE ──
            p.setFont('Helvetica-Bold', 11)
            p.drawString(220, 740 + y_offset, str(data_ecole[0]))
            p.setFont('Helvetica-Oblique', 9)
            p.drawString(220, 725 + y_offset, str(data_ecole[6]))

            # ── LIGNE SEPARATRICE ──
            p.line(140, 715 + y_offset, 440, 715 + y_offset)

            # ── ANNEE SCOLAIRE ──
            p.setFont('Helvetica-Bold', 11)
            p.drawString(150, 700 + y_offset, 'Année Scolaire :')
            p.setFont('Helvetica', 11)
            p.drawString(255, 700 + y_offset, str(data[1]))
            p.setFont('Helvetica-Bold',11)
            p.drawString(330, 700 + y_offset, 'Session : ')
            p.setFont('Helvetica',11)
            p.drawString(385, 700 + y_offset, str(ane))

            # ── TITRE RECU ──
            p.setFont('Helvetica-Bold', 12)
            p.rect(150, 673 + y_offset, 280, 18, stroke=True, fill=False)
            p.drawString(165, 677 + y_offset,f'RECU DE PAIEMENT N° {numero_recu}')

            # ── INFOS ELEVE ──
            p.setFont('Helvetica-Bold', 11)
            p.drawString(120, 650 + y_offset, 'Matricule :')
            p.setFont('Helvetica', 11)
            p.drawString(195, 650 + y_offset, str(data[2]))

            p.setFont('Helvetica-Bold', 11)
            p.drawString(120, 634 + y_offset, 'Nom :')
            p.setFont('Helvetica', 11)
            p.drawString(195, 634 + y_offset, str(data[4]))

            p.setFont('Helvetica-Bold', 11)
            p.drawString(120, 618 + y_offset, 'Prénoms :')
            p.setFont('Helvetica', 11)
            p.drawString(195, 618 + y_offset, str(data[5]))

            p.setFont('Helvetica-Bold', 11)
            p.drawString(120, 600 + y_offset, 'Classe :')
            p.setFont('Helvetica', 11)
            p.drawString(195, 600 + y_offset, str(data[3]))

            # Infos droite
            p.setFont('Helvetica-Bold', 11)
            p.drawString(340, 634 + y_offset, 'Tuteur :')
            p.setFont('Helvetica', 11)
            p.drawString(390, 634 + y_offset, str(data[6]))

            p.setFont('Helvetica-Bold', 11)
            p.drawString(340, 618 + y_offset, 'Contact :')
            p.setFont('Helvetica', 11)
            p.drawString(395, 618 + y_offset, str(data[7]))
            p.setFont('Helvetica-Bold', 11)
            p.drawString(340, 600 + y_offset, 'Email :')
            p.setFont('Helvetica', 11)
            p.drawString(395, 600 + y_offset, str(data[8]))


            # ── TABLEAU TRANCHE ──
            # Largeurs ajustées : total = 520 points
            col_x = [20, 155, 295, 405, 520]  # Positions X des séparateurs verticaux
            col_w = [135, 140, 110, 115]      # Largeurs des 4 colonnes

            # En-tête avec fond bleu et texte blanc
            p.setFillColor(colors.HexColor('#2980b9'))
            p.rect(20, 555 + y_offset, 500, 20, stroke=True, fill=True)
            p.setFillColor(colors.white)
            p.setFont('Helvetica-Bold', 10)
            p.drawString(25,  560 + y_offset, 'Tranche')
            p.drawString(160, 560 + y_offset, 'Montant tranche')
            p.drawString(300, 560 + y_offset, 'Montant Payé')
            p.drawString(410, 560 + y_offset, 'Reste à payer')
            
            # Remettre noir pour la ligne de données
            p.setFillColor(colors.black)
            p.setFont('Helvetica', 10)
            p.rect(20, 535 + y_offset, 500, 20, stroke=True, fill=False)
            p.drawString(25,  540 + y_offset, tranche_name)
            p.drawString(160, 540 + y_offset, montant_tranche_formate)
            p.drawString(300, 540 + y_offset, montant_paye_formate)
            p.drawString(410, 540 + y_offset, reste_formate)

            # Lignes verticales du tableau
            for x in col_x:
                p.line(x, 535 + y_offset, x, 575 + y_offset)
            
            # ── DATE ET SIGNATURE ──
            p.setFont('Helvetica-Bold', 11)
            p.drawString(375, 510 + y_offset, 'Conakry, le ')
            p.drawString(450, 510 + y_offset, datetime.now().strftime('%d/%m/%Y'))
            p.drawString(375, 475 + y_offset, 'Le Service Scolarité')
            p.drawString(375, 435 + y_offset, str(data_ecole[8]))

        # ── PREMIER EXEMPLAIRE ──
        draw_recu(0)

        # ── LIGNE SEPARATRICE ENTRE LES DEUX EXEMPLAIRES ──
        p.line(20, 420, 580, 420)

        # ── DEUXIEME EXEMPLAIRE ──
        draw_recu(-420)

        p.showPage()
        p.save()
        buffer.seek(0)

        # ── ENVOI EMAIL ──
        try:
            email = EmailMessage(
                subject='Reçu de paiement scolarité',
                body=f'Veuillez trouver votre reçu de paiement en pièce jointe.\n'
                     f'Cordialement.\n La Comptabilité : \n {data_ecole[8]}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[data[8]],
            )
            email.attach(f'Recu_paiement_{str(data[2])}.pdf', buffer.getvalue(), 'application/pdf')
            email.send()
            messages.success(request, 'Email envoyé avec succès!')
        except SMTPException:
            messages.warning(request, 'Erreur SMTP : impossible d\'envoyer l\'email.')
        except socket.gaierror:
            messages.warning(request, 'Pas de connexion internet. Email non envoyé.')
        except TimeoutError:
            messages.warning(request, 'Délai de connexion dépassé. Email non envoyé.')
        except Exception as e:
            messages.warning(request, f'Erreur inattendue : {str(e)}')

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=False, filename=f'Recu_paiement_{str(data[2])}.pdf', content_type='application/pdf')

@action_requise('menu_comptabilite')
def imprimerecuscolarite(request, idetat, nom_tranche, mont_paye):
    return HttpResponseRedirect(reverse('recupaiementscolarite',args=(idetat,nom_tranche,str(mont_paye),)))

@action_requise('menu_comptabilite')
def listepaiementmensuel(request):
    
    anne = {}
    cy = {}
    listepaiemensuel = {}
    t_premiere_tranche = {}
    t_deuxieme_tranche = {}
    t_reste_a_payer = {}
    t_paiement_annuel = {}

    total_tranche1 = 0
    total_tranche2 = 0
    total_reste_a_payer = 0
    total_paiement_annuel = 0

    anne = AnneeScolaire.objects.none()
    cy = CycleScolaire.objects.none()
    listepaiemensuel = EtatPaiementTranche.objects.none()

    mois = date.today()
    mois_actuel = mois.strftime('%m')
    listepaiemensuel = EtatPaiementTranche.objects.select_related('anneescolaire','mateleve','idclasse','idcycle').filter(date_paie__month=mois_actuel).order_by('-date_paie')

    t_premiere_tranche = EtatPaiementTranche.objects.filter(date_paie__month=mois_actuel).aggregate(pt=Sum('premiere_tranche')) # pt correspond à la clé du dictionnaire resultant de la requếte
    t_deuxieme_tranche = EtatPaiementTranche.objects.filter(date_paie__month=mois_actuel).aggregate(dt=Sum('deuxieme_tranche')) # dt de même
    t_reste_a_payer = EtatPaiementTranche.objects.filter(date_paie__month=mois_actuel).aggregate(tr=Sum('reste_a_payer'))
    t_paiement_annuel = EtatPaiementTranche.objects.filter(date_paie__month=mois_actuel).aggregate(ta=Sum('fscolarite')) # ta est ici la clé du dictionnaire correspondant au total des paiements annuels

    if t_premiere_tranche['pt'] is not None:
        total_tranche1 = t_premiere_tranche['pt']
    else:
        total_tranche1 = 0
    
    if t_deuxieme_tranche['dt'] is not None:
        total_tranche2 = t_deuxieme_tranche['dt']
    else:
        total_tranche2 = 0
    
    if t_reste_a_payer['tr'] is not None:
        total_reste_a_payer = t_reste_a_payer['tr']
    else:
        total_reste_a_payer = 0

    if t_paiement_annuel['ta'] is not None:
        total_paiement_annuel = t_paiement_annuel['ta']
    else:
        total_paiement_annuel = 0
    

    anne = AnneeScolaire.objects.all().order_by('id')
    cy = CycleScolaire.objects.all().order_by('id')

    paginepaie = Paginator(listepaiemensuel, 10)
    numpagepaie = request.GET.get('page')
    listepaiemensuel = paginepaie.get_page(numpagepaie)

    return render(request,'gComptabilite/liste_etat_paiement_scolarite.html',dict(ans=anne, cycles=cy, listepaiementmensuel=listepaiemensuel, total_tranche1=total_tranche1, total_tranche2=total_tranche2, total_reste_a_payer=total_reste_a_payer, tranche_paye=DEUX_TRANCHES_CHOICES, total_paiement_annuel=total_paiement_annuel))

@action_requise('menu_comptabilite')
def filtrelistepaiementclasse(request):

    anne = request.GET.get('annee_scolaire')
    clas = request.GET.get('id_classe')

    an = {}
    cy = {}
    t_premiere_tranche = {}
    t_deuxieme_tranche = {}
    t_reste_a_payer = {}
    t_paiement_annuel = {}

    total_tranche1 = 0
    total_tranche2 = 0
    total_reste_a_payer = 0
    total_paiement_annuel = 0

    an = AnneeScolaire.objects.none()
    cy = CycleScolaire.objects.none()

    listepaieclasse = {}
    listepaieclasse = EtatPaiementTranche.objects.none()

    listepaieclasse = EtatPaiementTranche.objects.select_related('anneescolaire','mateleve','idclasse','idcycle').filter(Q(anneescolaire__exact=anne),Q(idclasse__exact=clas)).order_by('-date_paie')

    t_premiere_tranche = EtatPaiementTranche.objects.select_related('anneescolaire','mateleve','idclasse','idcycle').filter(Q(anneescolaire__exact=anne),Q(idclasse__exact=clas)).aggregate(pt=Sum('premiere_tranche')) # pt correspond à la clé du dictionnaire resultant de la requếte

    t_deuxieme_tranche = EtatPaiementTranche.objects.select_related('anneescolaire','mateleve','idclasse','idcycle').filter(Q(anneescolaire__exact=anne),Q(idclasse__exact=clas)).aggregate(dt=Sum('deuxieme_tranche')) # dt de même

    t_reste_a_payer = EtatPaiementTranche.objects.select_related('anneescolaire','mateleve','idclasse','idcycle').filter(Q(anneescolaire__exact=anne),Q(idclasse__exact=clas)).aggregate(tr=Sum('reste_a_payer'))

    t_paiement_annuel = EtatPaiementTranche.objects.select_related('anneescolaire','mateleve','idclasse','idcycle').filter(Q(anneescolaire__exact=anne),Q(idclasse__exact=clas)).aggregate(ta=Sum('fscolarite'))

    if t_premiere_tranche['pt'] is not None:
        total_tranche1 = t_premiere_tranche['pt']
    else:
        total_tranche1 = 0
    
    if t_deuxieme_tranche['dt'] is not None:
        total_tranche2 = t_deuxieme_tranche['dt']
    else:
        total_tranche2 = 0
    
    if t_reste_a_payer['tr'] is not None:
        total_reste_a_payer = t_reste_a_payer['tr']
    else:
        total_reste_a_payer = 0

    if t_paiement_annuel['ta'] is not None:
        total_paiement_annuel = t_paiement_annuel['ta']
    else:
        total_paiement_annuel = 0

    an = AnneeScolaire.objects.all().order_by('id')
    cy = CycleScolaire.objects.all().order_by('id')

    paginepaie = Paginator(listepaieclasse, 10)
    numpagepaie = request.GET.get('page')
    listepaieclasse = paginepaie.get_page(numpagepaie)

    return render(request,'gComptabilite/liste_etat_paiement_scolarite.html',{'listepaiementclasse':listepaieclasse, 'ans': an, 'cycles': cy, 'total_tranche1': total_tranche1, 'total_tranche2': total_tranche2, 'total_reste_a_payer': total_reste_a_payer, 'tranche_paye': DEUX_TRANCHES_CHOICES, 'total_paiement_annuel': total_paiement_annuel})

@action_requise('compta_modifier')
def detailpaiementscolaire(request, idpaie):
    etatpaie = EtatPaiementTranche.objects.select_related('anneescolaire','mateleve','idclasse','idcycle').get(id=idpaie)
    return render(request,'gComptabilite/afficher_details_paiement_scolaire.html', dict(paie=etatpaie))

@action_requise('compta_modifier')
def editerpaiementscolaire(request, idpaie):
    etatpaie = EtatPaiementTranche.objects.select_related('anneescolaire','mateleve','idclasse','idcycle').get(id=idpaie)
    ans = AnneeScolaire.objects.all().order_by('id')
    cy = CycleScolaire.objects.all().order_by('id')
    return render(request,'gComptabilite/modifier_paiement_scolaire.html',dict(paie=etatpaie, tranche_paye=DEUX_TRANCHES_CHOICES, annee=ans, cycles=cy, modepaie=MODE_PAIEMENT_CHOICES))

@action_requise('compta_modifier')
def modifieretatpaiement(request, idpaie):

    p_tranche = 0
    d_tranche = 0
    mremise = 0
    fscol = 0

    if request.method == 'POST':
        etatpaie = EtatPaiementTranche.objects.get(id=idpaie)
        ans = request.POST.get('annee_scolaire')
        cycl = request.POST.get('cycle_scolaire')
        clas = request.POST.get('classe')
        mat = request.POST.get('matricule')
        nom_tranche = request.POST.get('nom_tranche')
        datepaie = request.POST.get('date_paiement')
        mremise = reformater_montant(request.POST.get('montant_remise'))
        modepaie = request.POST.get('mode_paiement')
        

        ane = AnneeScolaire.objects.get(id=ans)
        cy = CycleScolaire.objects.get(id=cycl)
        cl = Classe.objects.get(id=clas)
        matel = Eleve.objects.get(matricule=mat)

        etatpaie.anneescolaire = ane
        etatpaie.idcycle = cy
        etatpaie.idclasse = cl
        etatpaie.mateleve = matel
        etatpaie.date_paie = datetime.strptime(datepaie,'%Y-%m-%d')
        etatpaie.mode_paie = modepaie

        # Je vais recuperer les frais de la première tranche et deuxième tranche ainsi que le frais de la scolarité dans la table Classe
        fannuel = cl.frais_scolarite


        if nom_tranche == DEUX_TRANCHES_CHOICES[0][0]: # Si c'est la premiere tranche qui est selectionnee

            p_tranche = reformater_montant(request.POST.get('montant_premiere_tranche'))
            etatpaie.premiere_tranche = p_tranche

        elif nom_tranche == DEUX_TRANCHES_CHOICES[1][0]: # Si c'est la deuxieme tranche qui est selectionnee

            d_tranche = reformater_montant(request.POST.get('montant_deuxieme_tranche'))
            etatpaie.deuxieme_tranche = d_tranche


        fscol = (etatpaie.premiere_tranche + etatpaie.deuxieme_tranche) # Permet de calculer le paiement total effectué par l'élève
        etatpaie.fscolarite = fscol
        if mremise:
            etatpaie.reste_a_payer = (fannuel - fscol)- mremise # Le reste à payer annuel est le montant annuel dû moins le total de ses paiements oté de la remise
            etatpaie.m_rabais = mremise
        else:
            etatpaie.reste_a_payer = fannuel - fscol
        etatpaie.save()
        

        return redirect('../listepaiemensuel/')


    else:
        return redirect('../listepaiemensuel/')
    
@action_requise('compta_supprimer')
def supprimerpaiementscolaire(request, idpaie):
    etatpaie = EtatPaiementTranche.objects.get(id=idpaie)
    etatpaie.delete()
    return redirect('../listepaiemensuel/')

# Vue permettant de generer à partir de la fonction utilitaire le rapport des etats de paiement
@action_requise('menu_comptabilite')
def rapportpaiementtranche(request):

    anne = request.GET.get('annee')  
    cycl = request.GET.get('cycle')   
    clas = request.GET.get('classe')
    nom_tranche = request.GET.get('tranche')

    ec = Ecole.objects.count()
    if ec == 0:
        messages.error(request, 'Veuillez saisir les informations de l\'école')
    else:
        ecole = Ecole.objects.first()
        if ecole.logo_ecole:
            data_ecole = [ecole.nom_ecole, ecole.ville_ecole, ecole.prefect_commune,
                          ecole.telephone1, ecole.telephone2, ecole.logo_ecole.path,
                          ecole.devise_ecole, ecole.dsee, ecole.comptable]
        else:
            data_ecole = [ecole.nom_ecole, ecole.ville_ecole, ecole.prefect_commune,
                          ecole.telephone1, ecole.telephone2, 'Logo',
                          ecole.devise_ecole, ecole.dsee, ecole.comptable]

    # Titre du rapport
    titre = f"SUIVI DES PAIEMENTS DE LA {nom_tranche.upper()}"

    # Appel de la fonction utilitaire

    pdf_buffer = generer_rapport_paiement_scolarite(request,data_ecole=data_ecole,annee=anne, cycle=cycl, classe=clas, nom_tranche=nom_tranche, titre_rapport=titre)

    # 1. Vérification de l'erreur avant toute chose
    if pdf_buffer is None:
        return redirect('../listepaiemensuel/') # Redirection vers la liste des paiements

    # 2. TRÈS IMPORTANT : Remettre le curseur au début du buffer
    # Sinon, FileResponse lit à partir de la fin et votre PDF sera vide.
    pdf_buffer.seek(0)
    
    return FileResponse(pdf_buffer, as_attachment=False,
        filename=f'Situation_Paiement_{str(nom_tranche)}.pdf',
        content_type='application/pdf')



# Fonction utilitaire permettant de generer mon rapport des états de paiement
def generer_rapport_paiement_scolarite(request, data_ecole, annee, cycle, classe, nom_tranche, titre_rapport):
    """
    Génère un PDF de suivi des paiements pour une tranche donnée.
    Entête seulement sur la première page.
    Numéro de page à droite au format 'n°page """

    etatpaie = {}
    etatpaie = EtatPaiementTranche.objects.none()
    t_paye_t1 = {} # Permet de faire le cumul des montants de la première tranche
    t_paye_t2 = {} # Permet de faire le cumul des montants de la deuxième tranche
    total_paye_t1 = 0 # Contient le montant total des paiements de la première tranche
    total_paye_t2 = 0 # Contient le montant total des paiements de la deuxième tranche
    total_tranche = 0 
    total_reste = 0

    an = AnneeScolaire.objects.get(id=annee)
    cy = CycleScolaire.objects.get(id=cycle)
    cl = Classe.objects.get(id=classe)

    # --- 1. Récupération des données (commune aux deux passes) ---
    etatpaie = EtatPaiementTranche.objects.select_related(
        'anneescolaire', 'mateleve', 'idcycle', 'idclasse' 
    ).filter(Q(anneescolaire__exact=an), Q(idcycle__exact=cy),Q(idclasse__exact=cl)).order_by('mateleve__nom')

    t_paye_t1 = EtatPaiementTranche.objects.select_related('anneescolaire', 'mateleve', 'idcycle', 'idclasse').filter(Q(anneescolaire__exact=an), Q(idcycle__exact=cy),Q(idclasse__exact=cl)).aggregate(totalpaye=Sum('premiere_tranche'))

    t_paye_t2 = EtatPaiementTranche.objects.select_related('anneescolaire', 'mateleve', 'idcycle', 'idclasse').filter(Q(anneescolaire__exact=an), Q(idcycle__exact=cy),Q(idclasse__exact=cl)).aggregate(totalpaye=Sum('deuxieme_tranche'))

    if t_paye_t1['totalpaye'] is not None:
        total_paye_t1 = t_paye_t1['totalpaye']
    else:
        total_paye_t1 = 0

    if t_paye_t2['totalpaye'] is not None:
        total_paye_t2 = t_paye_t2['totalpaye']
    else:
        total_paye_t2 = 0

    effectif = etatpaie.count() # Permet de compter le nombre d'élèves de la classe sélectionnée

    if effectif == 0:
        messages.error(request,"Aucun élève trouvé pour les critères donnés.")
    else:
         
        # --- 2. Construction du tableau (identique) ---
        entetes = ['N°', 'Matricule', 'Prénoms', 'Nom', nom_tranche, 'Montant payé', 'Reste à payer', 'Date paiement']
        table_data = [entetes]

        for i, etat in enumerate(etatpaie, start=1):

            # Détermination de la tranche
            if nom_tranche == DEUX_TRANCHES_CHOICES[0][0]: # Si c'est la première tranche qui a été sélectionnée dans la pop-up
                montant_tranche = cl.tranche1 
                paye = etat.premiere_tranche or 0
                total_tranche = cl.tranche1*effectif

            elif nom_tranche == DEUX_TRANCHES_CHOICES[1][0]: # Si c'est la seconde tranche qui a été sélectionnée dans la pop-up
                montant_tranche = cl.tranche2
                paye = etat.deuxieme_tranche or 0
                total_tranche = cl.tranche2*effectif
            
            reste = montant_tranche - paye
            dpaie = etat.date_paie
            date_str = dpaie.strftime('%d-%m-%Y') if dpaie else ''

            table_data.append([
                str(i),
                etat.mateleve.matricule,
                etat.mateleve.prenom,
                etat.mateleve.nom,
                '{:,}'.format(montant_tranche),
                '{:,}'.format(paye),
                '{:,}'.format(reste),
                date_str,
            ])

        if nom_tranche == DEUX_TRANCHES_CHOICES[0][0]: # Si c'est la première tranche qui a été sélectionnée dans la pop-up

            total_reste = total_tranche - total_paye_t1    

            # Ligne des totaux
            table_data.append([
                'Totaux', '', '', '',
                '{:,}'.format(total_tranche),
                '{:,}'.format(total_paye_t1),
                '{:,}'.format(total_reste),
                ''
            ])
                    
        elif nom_tranche == DEUX_TRANCHES_CHOICES[1][0]: # Si c'est la seconde tranche qui a été sélectionnée

            total_reste = total_tranche - total_paye_t2

            # Ligne des totaux
            table_data.append([
                'Totaux', '', '', '',
                '{:,}'.format(total_tranche),
                '{:,}'.format(total_paye_t2),
                '{:,}'.format(total_reste),
                ''
            ])
        
        
        col_widths = [1.2*cm, 2.2*cm, 3.0*cm, 3.0*cm, 2.8*cm, 2.8*cm, 2.8*cm, 2.5*cm]
        table = Table(table_data, repeatRows=1, colWidths=col_widths)

        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2980b9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f5f5f5')]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTSIZE', (0, -1), (-1, -1), 9),
            ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
            ('SPAN', (0, -1), (3, -1)),   # ← fusionne les colonnes 0 à 3 (N°, Matricule, Prénoms, Nom) sur la ligne Totaux
        ])
        table.setStyle(style)


        # --- 3. Éléments du flux ---
        # NextPageTemplate bascule vers le template 'Suivantes' dès que la page 2 commence
        elements = [NextPageTemplate('Suivantes'), Spacer(1, 0.3*cm)]
        elements.append(table)
        elements.append(Spacer(1, 1.0*cm))

        style_signature = ParagraphStyle(
        'Signature', parent=getSampleStyleSheet()['Normal'],
        alignment=TA_RIGHT, fontName='Helvetica-Bold') # gras appliqué à tout le style

        date_str = datetime.now().strftime('%d-%m-%Y')   

        bloc_signature = [
            [Paragraph(f"Conakry, le {date_str}", style_signature)],
            [Spacer(1, 0.8*cm)], # ← espace ajouté entre la date et "Le Service Scolarité"
            [Paragraph("Le Service Scolarité", style_signature)],
            [Spacer(1, 1.5*cm)], # ← espace agrandi : laisse la place à la signature manuscrite avant le nom
            [Paragraph(str(data_ecole[8]) if len(data_ecole) > 8 and data_ecole[8] else '', style_signature)],
                    ]

        table_signature = RLTable(bloc_signature, colWidths=[A4[0] - 2*cm])  # même largeur que le cadre du contenu
        table_signature.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))

        elements.append(table_signature)

        
        def draw_entete(canvas_obj, doc):
            width, height = A4
            nom_ecole = data_ecole[0] if len(data_ecole) > 0 else ''
            ville = data_ecole[1] if len(data_ecole) > 1 else ''
            commune = data_ecole[2] if len(data_ecole) > 2 else ''
            tel1 = data_ecole[3] if len(data_ecole) > 3 else ''
            tel2 = data_ecole[4] if len(data_ecole) > 4 else ''
            logo_chemin = data_ecole[5] if len(data_ecole) > 5 else ''
            devise = data_ecole[6] if len(data_ecole) > 6 else ''
            dsee = data_ecole[7] if len(data_ecole) > 7 else ''

            canvas_obj.setFillColor(colors.black)
            canvas_obj.setFont('Helvetica-Bold', 10)
            canvas_obj.drawString(20, 815, 'MEPU-A')
            canvas_obj.drawString(20, 800, 'IRE : ')
            canvas_obj.setFont('Helvetica', 10)
            canvas_obj.drawString(55, 800, str(ville))
            canvas_obj.setFont('Helvetica-Bold', 10)
            canvas_obj.drawString(20, 787, 'DCE : ')
            canvas_obj.setFont('Helvetica', 10)
            canvas_obj.drawString(55, 787, str(commune))
            canvas_obj.setFont('Helvetica-Bold', 10)
            canvas_obj.drawString(20, 772, 'DSEE : ')
            canvas_obj.setFont('Helvetica', 10)
            canvas_obj.drawString(55, 772, str(dsee))
            canvas_obj.setFont('Helvetica-Bold', 10)
            canvas_obj.drawString(20, 757, 'TEL : ')
            canvas_obj.setFont('Helvetica', 10)
            canvas_obj.drawString(55, 757, f"{tel1} / {tel2}")

            if logo_chemin and logo_chemin != 'Logo':
                try:
                    img = Image.open(logo_chemin)
                    img = img.resize((90, 60), Image.LANCZOS)
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    logo_buffer = io.BytesIO()
                    img.save(logo_buffer, format='PNG')
                    logo_buffer.seek(0)
                    canvas_obj.drawImage(ImageReader(logo_buffer), 245, 770, 90, 60)
                except Exception:
                    pass

            canvas_obj.setFillColor('Red')
            canvas_obj.rect(449, 815, 30, 10, stroke=False, fill=True)
            canvas_obj.setFillColor('yellow')
            canvas_obj.rect(479, 815, 30, 10, stroke=False, fill=True)
            canvas_obj.setFillColor('green')
            canvas_obj.rect(509, 815, 30, 10, stroke=False, fill=True)
            canvas_obj.setFillColor(colors.black)

            canvas_obj.setFont('Helvetica-Bold', 10)
            canvas_obj.drawString(450, 800, 'République de Guinée')
            canvas_obj.setFont('Helvetica-Oblique', 9)
            canvas_obj.drawString(450, 785, 'Travail-Justice-Solidarité')

            canvas_obj.setFont('Helvetica-Bold', 12)
            nom_x = (width - canvas_obj.stringWidth(str(nom_ecole), 'Helvetica-Bold', 12)) / 2
            canvas_obj.drawString(nom_x, 740, str(nom_ecole))
            if devise:
                canvas_obj.setFont('Helvetica-Oblique', 9)
                devise_x = (width - canvas_obj.stringWidth(str(devise), 'Helvetica-Oblique', 9)) / 2
                canvas_obj.drawString(devise_x, 725, str(devise))

            canvas_obj.line(20, 715, 575, 715)

            titre = titre_rapport.upper()
            canvas_obj.setFont('Helvetica-Bold', 12)
            titre_x = (width - canvas_obj.stringWidth(titre, 'Helvetica-Bold', 12)) / 2
            canvas_obj.drawString(titre_x, 700, titre)
            canvas_obj.line(80, 694, 515, 694)

            annee_str = an.descript_annee if an else ''
            session = annee_str.split('-')[-1] if '-' in annee_str else annee_str
            canvas_obj.setFont('Helvetica-Bold', 11)
            canvas_obj.drawString(180, 680, 'Année Scolaire : ')
            canvas_obj.setFont('Helvetica', 11)
            canvas_obj.drawString(300, 680, annee_str)
            canvas_obj.setFont('Helvetica-Bold', 11)
            canvas_obj.drawString(400, 680, 'Session : ')
            canvas_obj.setFont('Helvetica', 11)
            canvas_obj.drawString(460, 680, session)

            Y_CYCLE_CLASSE = 650   # décalé de 664 à 650 (14pt plus bas ; ajustez selon le rendu voulu)

            canvas_obj.setFont('Helvetica-Bold', 11)
            canvas_obj.drawString(20, Y_CYCLE_CLASSE, 'Cycle : ')
            canvas_obj.setFont('Helvetica', 11)
            canvas_obj.drawString(60, Y_CYCLE_CLASSE, str(cy.cycle) if cy else '')
            canvas_obj.setFont('Helvetica-Bold', 11)
            canvas_obj.drawString(150, Y_CYCLE_CLASSE, 'Classe : ')
            canvas_obj.setFont('Helvetica', 11)
            canvas_obj.drawString(200, Y_CYCLE_CLASSE, str(cl.nom_classe) if cl else '')
            canvas_obj.setFont('Helvetica-Bold', 11)
            canvas_obj.drawString(310, Y_CYCLE_CLASSE, 'Effectif de la classe : ')
            canvas_obj.setFillColor(colors.red)
            canvas_obj.setFont('Helvetica-Bold', 11)
            canvas_obj.drawString(450, Y_CYCLE_CLASSE, str(effectif))
            canvas_obj.setFillColor(colors.black)

        # --- 5. Numéro de page (sur toutes les pages) ---
        def draw_page_number(canvas_obj, doc):
            canvas_obj.saveState()
            canvas_obj.setFont('Helvetica', 8)
            x = A4[0] - 1.5*cm
            y = 1.0*cm
            canvas_obj.drawRightString(x, y, f"Page {doc.page}")
            canvas_obj.restoreState()

        def on_first_page(canvas_obj, doc):
            draw_entete(canvas_obj, doc)
            draw_page_number(canvas_obj, doc)

        def on_later_pages(canvas_obj, doc):
            draw_page_number(canvas_obj, doc)

        # --- 6. Construction avec deux PageTemplate ---
        buffer = io.BytesIO()

        marge_gauche_droite = 1.0*cm
        marge_bas = 1.0*cm
        largeur_frame = A4[0] - 2*marge_gauche_droite

        # Page 1 : cadre qui commence sous l'entête (y=650pt depuis le bas, avec marge de sécurité)

        y_fin_entete = 636   # 650 - 14, pour garder la même marge de sécurité qu'avant
        hauteur_frame_page1 = y_fin_entete - marge_bas
        frame_page1 = Frame(
            marge_gauche_droite, marge_bas,
            largeur_frame, hauteur_frame_page1,
            id='page1', showBoundary=0
        )

        # Pages suivantes : cadre classique, marge haute réduite
        frame_suivantes = Frame(
            marge_gauche_droite, marge_bas,
            largeur_frame, A4[1] - marge_bas - 1.5*cm,
            id='suivantes', showBoundary=0
        )

        doc = BaseDocTemplate(buffer, 
                            pagesize=A4,
                            title='Situation des Paiements par tranche')
        doc.addPageTemplates([
            PageTemplate(id='Premiere', frames=frame_page1, onPage=on_first_page),
            PageTemplate(id='Suivantes', frames=frame_suivantes, onPage=on_later_pages),
        ])

        doc.build(elements)
        buffer.seek(0)
        return buffer

