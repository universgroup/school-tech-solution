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
from PIL import Image

from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings
import io  # Librairie contenant les methodes utilisant les péripheriques d'entrées/sorties

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


def listerecette(request):
      
    mois_courant = datetime.strftime(datetime.now(),'%m') # Je recupere le numero du mois en cours en vue de filtrer les operations conformement a cela
    mactu = datetime.strftime(datetime.now(),'%B') # Le nom du mois en Toute lettre (Mars ici)
    
    cais = Caisse.objects.filter(Q(type_operation=TYPE_OPERATION_CAISSE_CHOICES[1][1]),
                                 Q(date_operation__month=mois_courant)).order_by(
        '-date_operation')  # Affiche la situation de la caisse des recettes par ordre décroissant de la date
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


def detailscaisserecette(request, idcais):
    cais = Caisse.objects.get(id=idcais)
    return render(request, 'gComptabilite/afficher_details_caisse_scolarite.html', dict(cais=cais))


def editercaisserecette(request, idcais):
    cais = Caisse.objects.get(id=idcais)
    return render(request, 'gComptabilite/modifier_caisse_scolarite.html', dict(cais=cais))


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
        '-date_operation')
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
        '-date_operation')
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


    paginecais = Paginator(recette, 10)
    numpagecais = request.GET.get('page')
    recette = paginecais.get_page(numpagecais)
    return render(request, 'gComptabilite/liste_recettes.html',
                  dict(recette=recette, total_entree=total_entree, total_sortie=total_sortie, solde_dispo=solde_dispo, ddebut=debut, dfin=fin))


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


def listedepense(request):
  
    mois_courant = datetime.strftime(datetime.now(),'%m') # Je recupere le numero du mois en cours en vue de filtrer les operations conformement a cela
    mactu = datetime.strftime(datetime.now(),'%B') # Le nom du mois en Toute lettre (Mars ici)
    
    cais = Caisse.objects.filter(Q(type_operation=TYPE_OPERATION_CAISSE_CHOICES[2][1]),
                                 Q(date_operation__month=mois_courant)).order_by(
        '-date_operation')  # Affiche la situation de la caisse des recettes par ordre décroissant de la date
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
        '-date_operation')

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
        '-date_operation')

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
            

    paginecais = Paginator(depense, 10)
    numpagecais = request.GET.get('page')
    depense = paginecais.get_page(numpagecais)

    return render(request, 'gComptabilite/liste_depenses.html',
                  dict(depense=depense, total_entree=total_entree, total_sortie=total_sortie, solde_dispo=solde_dispo, ddebut=debut, dfin=fin))


def detailsdepense(request, id):
    depense = Caisse.objects.get(id=id)
    return render(request, 'gComptabilite/afficher_details_depense.html', dict(depense=depense))


def editerdepense(request, id):
    depense = Caisse.objects.get(id=id)
    return render(request, 'gComptabilite/modifier_depense.html', {'depense': depense})


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


def supprimerdepense(request, pk):
    depense = Caisse.objects.get(id=pk)
    depense.delete()
    return redirect('../listedepense/')

# Début de la Gestion des paiements de la scolarité

# Cette fonction me permet de charger la liste des élèves inscrits dans une classe donnée aucours d'une année
# scolaire donnée
def chargerlisteelevepaiement(request):
    ane = request.GET.get('anneesco') # anneesco est la valeur renvoyée depuis la fonction JQuery dans le template paiement_scolarite.html
    clas = request.GET.get('id_classe') # id_classe est recupérée depuis la fonction JQuery
    el = Inscription.objects.select_related('annee_scolaire', 'mateleve', 'idcycle', 'idclasse').filter(
        Q(annee_scolaire=ane), Q(idclasse=clas))
    return render(request, 'gComptabilite/liste_eleve_classe_cycle_paiement.html', dict(eleve=el))


# La fonction chargerlisteclasse m'a permis de gerer l'affichage des classes selon le cycle selectionné lors de
# l'inscription associé au JQuery en Front-end
def chargerlisteclassepaiement(request):
    cy = request.GET.get('idcycle')
    clas = Classe.objects.filter(idcycle=cy).all()
    context = {'clas': clas}
    return render(request, 'gComptabilite/liste_classe_cycle_paiement.html', context)

# Cette fonction me permet de charger les infos de l'élève sélectionné lors de la reinscription à savoir le prénom, le nom et la photo
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


# Fonction permettant de valider le paiement de la scolarite
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

    annee = AnneeScolaire.objects.none()
    cycle = CycleScolaire.objects.none()

    if request.method == 'POST':
        
        ane = request.POST.get('annee_scolaire')
        clas = request.POST.get('classe')
        mat = request.POST.get('matricule')
        cycl = request.POST.get('cycle')

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
               
        if nom_tranche == DEUX_TRANCHES_CHOICES[0][0]: # Permet de verifier la première tranche
            
            if p_tranche < t1: # Je verifie que le montant de la première tranche payée est inférieur au montant de la tranche 1 défini dans la table classe
                
                etatpaie.anneescolaire = anes
                etatpaie.idclasse = cls
                etatpaie.mateleve = matel
                etatpaie.idcycle = cy
                etatpaie.date_paie = request.POST['date_paiement']                
                etatpaie.premiere_tranche = p_tranche + mont_paye # Le montant de la première tranche sera égal au montant initial payé + le nouveau montant payé pour cette tranche 

                fscol = (etatpaie.premiere_tranche + etatpaie.deuxieme_tranche)- mremise # Permet de calculer le paiement total effectué par l'élève
                etatpaie.fscolarite = fscol
                etatpaie.reste_a_payer = fannuel - fscol # Le reste à payer annuel est le montant annuel dû moins le total de ses paiements
                etatpaie.m_rabais = mremise
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

            else:
                messages.error(request,'La première tranche est déjà complète. Veuillez passer à la seconde tranche !!!')
        
        elif nom_tranche == DEUX_TRANCHES_CHOICES[1][0]: # Permet de vérifier la deuxième tranche
            if p_tranche < t1: # Je verifie ici si la première tranche n'est pas bouclée alors je renvoie une alerte pour completer celle-ci
                messages.error(request,'Vous devez finaliser le paiement de la première tranche avant de passer à la suivante')
            else:
                if d_tranche < t2:

                    etatpaie.anneescolaire = anes
                    etatpaie.idclasse = cls
                    etatpaie.mateleve = matel
                    etatpaie.idcycle = cy
                    etatpaie.date_paie = request.POST['date_paiement'] 
                    etatpaie.deuxieme_tranche = d_tranche + mont_paye # Le montant de la deuxième tranche sera égal au montant initial payé + le nouveau montant payé pour cette tranche

                    fscol = (etatpaie.premiere_tranche + etatpaie.deuxieme_tranche)- mremise # Permet de calculer le paiement total effectué par l'élève
                    etatpaie.fscolarite = fscol
                    etatpaie.reste_a_payer = fannuel - fscol # Le reste à payer annuel est le montant annuel dû moins le total de ses paiements
                    etatpaie.m_rabais = mremise
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

                else:
                    messages.error(request,'La scolarité est déjà complète!! cet élève ne doit plus rien pour cette année scolaire')
        
        

        annee = AnneeScolaire.objects.all().order_by('id')
        cycle = CycleScolaire.objects.all().order_by('id')

            
    else:
        annee = AnneeScolaire.objects.all().order_by('id')
        cycle = CycleScolaire.objects.all().order_by('id')    
    


    return render(request,'gComptabilite/paiement_scolarite.html',dict(ans=annee,cycles=cycle, tranche_paye=DEUX_TRANCHES_CHOICES))


def recupaiementscolarite(request, idetat, nom_tranche, mont_paye):
    # Et là je tente de recuperer les données d'identification de l'école
    ec = Ecole.objects.count()
    if ec==0:
        messages.error(request,'Veuillez saisir les informations de l\'école')
    else:
        ecole = Ecole.objects.get(id=1)
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
            montant_tranche = etatpaie.idclasse.tranche1
        elif nom_tranche == DEUX_TRANCHES_CHOICES[1][0]: # Si c'est la deuxième tranche, je recupère le montant correspondant dans la table classe
            montant_tranche = etatpaie.idclasse.tranche2

        montant_paye     = Decimal(mont_paye)
        reste_a_payer     = montant_tranche - (etatpaie.fscolarite + montant_paye)
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
            p.drawString(200, 740 + y_offset, str(data_ecole[0]))
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
            p.drawString(25,  540 + y_offset, nom_tranche)
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
            p.drawString(375, 475 + y_offset, 'La Comptabilité')
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
                     f'Cordialement.\nLa Comptabilité : {data_ecole[8]}',
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


def imprimerecuscolarite(request, idetat, nom_tranche, mont_paye):
    return HttpResponseRedirect(reverse('recupaiementscolarite',args=(idetat,nom_tranche,str(mont_paye),)))


def listepaiementmensuel(request):
    
    anne = {}
    cy = {}
    listepaiemensuel = {}
    t_premiere_tranche = {}
    t_deuxieme_tranche = {}
    t_reste_a_payer = {}

    total_tranche1 = 0
    total_tranche2 = 0
    total_reste_a_payer = 0

    anne = AnneeScolaire.objects.none()
    cy = CycleScolaire.objects.none()
    listepaiemensuel = EtatPaiementTranche.objects.none()

    mois = date.today()
    mois_actuel = mois.strftime('%m')
    listepaiemensuel = EtatPaiementTranche.objects.select_related('anneescolaire','mateleve','idclasse','idcycle').filter(date_paie__month=mois_actuel).order_by('-date_paie')

    t_premiere_tranche = EtatPaiementTranche.objects.filter(date_paie__month=mois_actuel).aggregate(pt=Sum('premiere_tranche')) # pt correspond à la clé du dictionnaire resultant de la requếte
    t_deuxieme_tranche = EtatPaiementTranche.objects.filter(date_paie__month=mois_actuel).aggregate(dt=Sum('deuxieme_tranche')) # dt de même
    t_reste_a_payer = EtatPaiementTranche.objects.filter(date_paie__month=mois_actuel).aggregate(tr=Sum('reste_a_payer'))

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
    

    anne = AnneeScolaire.objects.all().order_by('id')
    cy = CycleScolaire.objects.all().order_by('id')

    paginepaie = Paginator(listepaiemensuel, 10)
    numpagepaie = request.GET.get('page')
    listepaiemensuel = paginepaie.get_page(numpagepaie)

    return render(request,'gComptabilite/liste_etat_paiement_scolarite.html',dict(ans=anne, cycles=cy, listepaiementmensuel=listepaiemensuel, total_tranche1=total_tranche1, total_tranche2=total_tranche2, total_reste_a_payer=total_reste_a_payer))


def filtrelistepaiementclasse(request):

    anne = request.GET.get('annee_scolaire')
    clas = request.GET.get('id_classe')

    an = {}
    cy = {}
    t_premiere_tranche = {}
    t_deuxieme_tranche = {}
    t_reste_a_payer = {}

    total_tranche1 = 0
    total_tranche2 = 0
    total_reste_a_payer = 0

    an = AnneeScolaire.objects.none()
    cy = CycleScolaire.objects.none()

    listepaieclasse = {}
    listepaieclasse = EtatPaiementTranche.objects.none()

    listepaieclasse = EtatPaiementTranche.objects.select_related('anneescolaire','mateleve','idclasse','idcycle').filter(Q(anneescolaire__exact=anne),Q(idclasse__exact=clas)).order_by('-date_paie')

    t_premiere_tranche = EtatPaiementTranche.objects.select_related('anneescolaire','mateleve','idclasse','idcycle').filter(Q(anneescolaire__exact=anne),Q(idclasse__exact=clas)).aggregate(pt=Sum('premiere_tranche')) # pt correspond à la clé du dictionnaire resultant de la requếte

    t_deuxieme_tranche = EtatPaiementTranche.objects.select_related('anneescolaire','mateleve','idclasse','idcycle').filter(Q(anneescolaire__exact=anne),Q(idclasse__exact=clas)).aggregate(dt=Sum('deuxieme_tranche')) # dt de même

    t_reste_a_payer = EtatPaiementTranche.objects.select_related('anneescolaire','mateleve','idclasse','idcycle').filter(Q(anneescolaire__exact=anne),Q(idclasse__exact=clas)).aggregate(tr=Sum('reste_a_payer'))

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

    an = AnneeScolaire.objects.all().order_by('id')
    cy = CycleScolaire.objects.all().order_by('id')

    paginepaie = Paginator(listepaieclasse, 10)
    numpagepaie = request.GET.get('page')
    listepaieclasse = paginepaie.get_page(numpagepaie)

    return render(request,'gComptabilite/liste_etat_paiement_scolarite.html',{'listepaiementclasse':listepaieclasse, 'ans': an, 'cycles': cy, 'total_tranche1': total_tranche1, 'total_tranche2': total_tranche2, 'total_reste_a_payer': total_reste_a_payer})

def detailpaiementscolaire(request, idpaie):
    etatpaie = EtatPaiementTranche.objects.select_related('anneescolaire','mateleve','idclasse','idcycle').get(id=idpaie)
    return render(request,'gComptabilite/afficher_details_paiement_scolaire.html', dict(paie=etatpaie))

def editerpaiementscolaire(request, idpaie):
    etatpaie = EtatPaiementTranche.objects.select_related('anneescolaire','mateleve','idclasse','idcycle').get(id=idpaie)
    return render(request,'gComptabilite/modifier_paiement_scolaire.html',dict(paie=etatpaie, tranche_paye=DEUX_TRANCHES_CHOICES))

def supprimerpaiementscolaire(request, idpaie):
    etatpaie = EtatPaiementTranche.objects.get(id=idpaie)
    etatpaie.delete()
    return redirect('../listepaiemensuel/')

    








    




        
