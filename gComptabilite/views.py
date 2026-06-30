from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator

from .models import *
from .forms import *
from decimal import Decimal
from django.db.models import Sum, Q
from gAdministration.models import AnneeScolaire, Historique
from django.utils.datastructures import MultiValueDictKeyError
from datetime import datetime

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

            if request.FILES.get('piece_jointe') != '':
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
