from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator  # Utilisé dans la gestion des paginations des différentes listes de données
from django.utils.datastructures import MultiValueDictKeyError

from datetime import datetime, date  # Utilisé pour recuperer l'année courante dans la generation des matricules des élèves
from django.db.models import Q, Max, \
    Sum  # Permet de faire des requêtes avec les opérateurs And (,) et les opérateurs OR (|)
import io  # Librairie contenant les methodes utilisant les péripheriques d'entrées/sorties
from django.http import FileResponse, HttpResponseRedirect, JsonResponse

from reportlab.pdfgen import canvas
#from reportlab.platypus.tables import Table, TableStyle  # Permet de generer des tableaux (matrices) de données
from reportlab.lib import colors  # Contient les méthodes/fonctions de gestion des couleurs
from reportlab.lib.utils import ImageReader
from PIL import Image

from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings
import socket
from smtplib import SMTPException

from .models import *
from .forms import *
from gComptabilite.models import *
from gComptabilite.views import affichersoldecaisse
from gAdministration.models import AnneeScolaire, CycleScolaire, Classe, Ecole


# Create your views here.
# GESTION DES INSCRIPTIONS DES ELEVES

def enregistrereleve(request):
    mateleve = ''
    nom_eleve = ''
    pren_eleve = ''
    
    if request.method == 'POST':

        # 1ère Partie du formulaire (Tabpage 1) : Validation des données personnelles de l'élève
        formeleve = FormEleve(request.POST)
        if formeleve.is_valid():
            # Ici j'enregistre les informations personnelles de l'élève à inscrire
            ansco = datetime.now().strftime('%Y')  # Je recupère uniquement l'année de la date courante
            ane = ansco[2:4]  # Permet de recuperer les deux derniers caractères de l'année courante
            num_ordre = 0

            if Eleve.objects.count() == 0:
                num_ordre = 1
            else:
                dernier = Eleve.objects.aggregate(DernierID=Max(
                    'ideleve'))  # Permet de recuperer le dernier ID candidat augmenté de 1 quand il y a au moins
                # un enregistrement dans la table sinon le numero ordre = 1
                num_ordre = dernier['DernierID'] + 1

            if num_ordre < 10:
                mateleve = ane + '00' + str(num_ordre)
            elif num_ordre < 100:
                mateleve = ane + '0' + str(num_ordre)
            elif num_ordre < 1000:
                mateleve = ane + '0' + str(num_ordre)
            elif num_ordre < 10000:
                mateleve = ane + '0' + str(num_ordre)

            # Le code suivant donne le même resultat que celui actuellement actif plus bas
            # m = mateleve
            # nom = request.POST.get('nom')
            # prenom = request.POST.get('prenom')
            # sexe_personnel = request.POST.get('sexe_eleve')
            # pere = request.POST.get('pere')
            # mere = request.POST.get('mere')
            # tuteur = request.POST.get('tuteur')
            # contact_parent = request.POST.get('contact_parent')
            # adresse = request.POST.get('adresse')
            # ecole_origine = request.POST.get('ecole_origine')
            # photo_eleve = request.FILES.get('photo_eleve')
            # datenaissance = request.POST.get('datenaissance')
            # lieu_naissance = request.POST.get('lieu_naissance')
            # date_arrivee = request.POST.get('date_arrivee')
            # pays_naissance = request.POST.get('pays_naissance')
            # eleve = Eleve(matricule=m, nom=nom, prenom=prenom, sexe_eleve=sexe_personnel, pere=pere, mere=mere, tuteur=tuteur,
            #               contact_parent=contact_parent, adresse=adresse, ecole_origine=ecole_origine,
            #               photo_eleve=photo_eleve, datenaissance=datenaissance, lieu_naissance=lieu_naissance,
            #               date_arrivee=date_arrivee, pays_naissance=pays_naissance)
            # eleve.save()

            eleve = Eleve()  # Je crée une nouvelle instance de la classe Eleve en appelant son constructeur par défaut
            eleve.ideleve = num_ordre
            eleve.matricule = mateleve
            
            nom_eleve = request.POST['nom'] # Je recupere le nom saisi en vu de le transformer en majuscule
            pren_eleve = request.POST['prenom'] # Je recupere le prenom saisi en vue de le transformer en Caractere capital
            
            eleve.nom = nom_eleve.upper() # ici en majuscule entierement
            eleve.prenom = pren_eleve.capitalize() # Premiere lettre en majuscule
            
            eleve.sexe_eleve = request.POST['sexe_eleve']
            eleve.pere = request.POST['pere']
            eleve.mere = request.POST['mere']
            eleve.tuteur = request.POST['tuteur']
            eleve.contact_pere = request.POST['contact_pere']
            eleve.contact_mere = request.POST['contact_mere']
            eleve.email_pere = request.POST['email_pere']
            eleve.email_mere = request.POST['email_mere']
            eleve.profes_pere = request.POST['profes_pere']
            eleve.profes_mere = request.POST['profes_mere']
            eleve.personne_contact = request.POST['personne_contact']
            eleve.adresse = request.POST['adresse']
            eleve.ecole_origine = request.POST['ecole_origine']
            
            #try:
            if request.FILES.get('photo_eleve'):
                    eleve.photo_eleve = request.FILES.get('photo_eleve')
            #except MultiValueDictKeyError:
            #    pass

            eleve.datenaissance = request.POST['datenaissance']
            eleve.lieu_naissance = request.POST['lieu_naissance']
            eleve.date_arrivee = request.POST['date_arrivee']
            eleve.pays_naissance = request.POST['pays_naissance']  
            eleve.save()  # Permet de valider l'enregistrement des informations de l'élève

            # messages.success(request, 'Informations élève validées avec succès')
            #return redirect('inscriptioneleve', mat=mateleve)

        # 2ème Partie (Tabpage 2) : Validation de l'inscription de l'élève
        forminscrip = FormInscription(request.POST)
        if forminscrip.is_valid():
                ansco = request.POST.get('annee_scolaire')  # Je recupère ici l'ID de l'année scolaire selectionnée
                idclas = request.POST.get('idclasse')  # Ici l'ID de la Classe selectionnée
                idcy = request.POST.get('idcycle')  # Ici l'ID du cycle selectionné
                

                # Je fais ensuite des requêtes sur les quatre tables en vue de recuperer les identifiants à inserer dans
                # la table inscription
                an = AnneeScolaire.objects.get(id=ansco)
                cl = Classe.objects.get(id=idclas)
                cy = CycleScolaire.objects.get(id=idcy)
                el = Eleve.objects.get(matricule=mateleve)

                # Je valide enfin l'inscription de l'elève enregistré
                inscrip = Inscription(annee_scolaire=an, mateleve=el, idclasse=cl, idcycle=cy)
                inscrip.save()

                # Ici je vais recuperer les frais d'inscription de la classe selectionnée
                frais = cl.frais_inscription
                # Et la je vais actualiser le dernier solde caisse en appellant la fonction affichersoldecaisse
                soldecaisse = affichersoldecaisse()
                # Je vais enregistrer ensuite l'opération dans la table caisse
                cais = Caisse()
                cais.type_operation = TYPE_OPERATION_CAISSE_CHOICES[1][1]
                cais.libelle_operation = 'Paiement des frais inscription de l\'élève:  {},  {} , {} '.format(
                    el.matricule, el.nom, el.prenom)
                cais.montant_encaisse = Decimal(frais)
                cais.anscolaire = an
                cais.categ_depense = CATEGORIE_RECETTE_CHOICES[1][1]
                cais.solde_actuel = Decimal(soldecaisse) + Decimal(frais)
                cais.date_operation = date.today() # Recupère la date du système en YYYY-MM-dd
                cais.save()

                # Ici je vais enregistrer les frais d'inscription de l'élève dans son etat de paiement de la scolarité
                etatscol = EtatPaiementTranche()
                etatscol.anneescolaire = an
                etatscol.idcycle = cy
                etatscol.idclasse = cl
                etatscol.mateleve = el
                etatscol.inscription = Decimal(frais)
                etatscol.date_paie = date.today()
                etatscol.save()

                # Ici je vais enregistrer l'evenement dans la table Historique
                his = Historique()
                his.nature_operation = 'Inscription'
                his.detail_operation = 'Inscription de l\'élève de matricule : {}, {}, {}'.format(
                    el.matricule, el.nom, el.prenom)
                his.user_login = 'contact@universtechgroup.com'
                his.poste_travail = ''
                his.save()

                messages.success(request, 'Inscription validée avec succès')

                # Je vide les champs après validation

                formeleve = FormEleve()
                forminscrit = FormInscription()

                # Ici je vais recuperer le dernier ID validé de l'Inscription
                idi = Inscription.objects.latest(
                'id')  # Cette instruction permet de recuperer le dernier record suivant l'id
                lastid = idi.id  # Permet de recuperer l'ID de ce dernier record
                return HttpResponseRedirect(reverse('recuinscription',
                                                args=(
                                                    lastid,)))  # Je redirige l'utilisateur vers l'impression du recu d'inscription (PDF)
           

    else:
        # Ici je renvoie dans le template les deux formulaires de saisie qui étaient jusque là separés au demarrage de celui-ci.
        # La raison est simple: Utiliser un tabpage pour gérer la saisie des données personnelles de l'élève et la validation de l'inscription
        formeleve = FormEleve()
        forminscrit = FormInscription()
    return render(request, 'gEleve/inscription_eleve.html', dict(form=formeleve,form_inscrit=forminscrit))


# La fonction chargerlisteclasse m'a permis de gerer l'affichage des classes selon le cycle selectionné lors de
# l'inscription associé au JQuery en Front-end
def chargerlisteclasse(request):
    cy = request.GET.get('idcycle')
    clas = Classe.objects.filter(idcycle=cy).all()
    context = {'clas': clas}
    return render(request, 'gEleve/charger_liste_classe_cycle.html', context)


# Permet d'afficher la liste générale des élèves (registre de matriculation)
def registrematricule(request):
    
    liste = Inscription.objects.select_related('annee_scolaire', 'mateleve', 'idcycle', 'idclasse').all().order_by(
        'idcycle')
    ansc = AnneeScolaire.objects.all().order_by('descript_annee')
    cycles = CycleScolaire.objects.all().order_by('id')
    # Ici je calcule les effectifs totaux des eleves inscrits
    effectif_total = liste.count()
    effectif_total_garcons = liste.filter(mateleve__sexe_eleve=SEXE_ELEVE_CHOICES[1][1]).count()
    effectif_total_filles = liste.filter(mateleve__sexe_eleve=SEXE_ELEVE_CHOICES[2][1]).count()

    pagineinscrit = Paginator(liste, 10)
    numpageinscrit = request.GET.get('page')
    liste = pagineinscrit.get_page(numpageinscrit)
    return render(request, 'gEleve/liste_generale_eleves.html',
                  dict(listegenerale=liste, ansc=ansc, cycles=cycles, effectif_total=effectif_total,
                       effectif_total_garcons=effectif_total_garcons, effectif_total_filles=effectif_total_filles))


def detailsinscription(request, pkins):
    ins = Inscription.objects.select_related('annee_scolaire', 'mateleve', 'idcycle', 'idclasse').get(id=pkins)
    return render(request, 'gEleve/afficher_details_inscription.html', dict(ins=ins))


def editerinscription(request, pk):
    ins = Inscription.objects.select_related('annee_scolaire', 'mateleve', 'idcycle', 'idclasse').get(id=pk)
    ans = AnneeScolaire.objects.all().order_by('id')
    cy = CycleScolaire.objects.all().order_by('id')
    cl = Classe.objects.all().order_by('id')

    return render(request, 'gEleve/modifier_inscription.html', dict(ins=ins, annee=ans, cycle=cy, clas=cl))


def modifierinscription(request, idins, mat):
    if request.method == 'POST':
        inscri = Inscription.objects.get(id=idins)
        inscri.date_inscription = request.POST.get('date_inscription')

        
        ansco = request.POST.get('ansco')  # Je recupère ici l'ID de l'année scolaire selectionnée
        idclas = request.POST.get('classe')  # Ici l'ID de la Classe selectionnée
        idcy = request.POST.get('cycle')  # Ici l'ID du cycle selectionné
                
        # Je fais ensuite des requêtes sur les quatre tables en vue de recuperer les identifiants à inserer dans
        # la table inscription
        an = AnneeScolaire.objects.get(id=ansco)
        cl = Classe.objects.get(id=idclas)
        cy = CycleScolaire.objects.get(id=idcy)

        # J'enregistre maintenant ces ID dans la table Inscription
        inscri.annee_scolaire = an
        inscri.idclasse = cl
        inscri.idcycle = cy
        inscri.save()

        dnais = request.POST.get('datenaiss')
        dentree = request.POST.get('date_entree')

        el = Eleve.objects.get(matricule=mat)
        el.nom = request.POST.get('nom')
        el.prenom = request.POST.get('prenom')
        el.sexe_eleve = request.POST.get('sexe_eleve')
        el.pere = request.POST.get('pere')
        el.mere = request.POST.get('mere')
        el.tuteur = request.POST.get('tuteur')
        el.contact_pere = request.POST.get('contact_pere')
        el.contact_mere = request.POST.get('contact_mere')
        el.email_pere = request.POST.get('email_pere')
        el.email_mere = request.POST.get('email_mere')
        el.profes_pere = request.POST.get('profes_pere')
        el.profes_mere = request.POST.get('profes_mere')
        el.personne_contact = request.POST.get('personne_contact')
        el.adresse = request.POST.get('adresse')
        el.ecole_origine = request.POST.get('ecole_origine')
        el.datenaissance = datetime.strptime(dnais,'%Y-%m-%d')
        el.lieu_naissance = request.POST.get('lieunais')
        el.date_arrivee = datetime.strptime(dentree,'%Y-%m-%d')
        el.pays_naissance = request.POST.get('pays_naiss')

        if request.FILES.get('photoel'):
            el.photo_eleve = request.FILES.get('photoel')
 
        el.save()
        return redirect('chargeranneecourante')
    else:
        return redirect('chargeranneecourante')


def supprimerinscription(request, pkins):
    insc = Inscription.objects.get(id=pkins)
    insc.delete()
    messages.success(request, 'Inscription supprimée avec succès')
    return redirect('../chargeranneecourante/')


# Fonctions me permettant de filtrer la liste des inscrits par matricule, par classe, par nom de famille
def filtrelistegenerale(request):
    listeins = {}
    listeinsclasse = {}
    listeinsnp = {}
    effectif_total = 0
    effectif_total_garcons = 0
    effectif_total_filles = 0

    mat = request.GET.get('matricule')
    idclass = request.GET.get('classe')
    idcy = request.GET.get('cycle')
    idansc = request.GET.get('annee_scolaire')
    np = request.GET.get('nomeleve')

    listeins = Inscription.objects.none()
    listeinsclasse = Inscription.objects.none()
    listeinsnp = Inscription.objects.none()

    if mat != '' and mat is not None:

        listeins = Inscription.objects.select_related('annee_scolaire', 'mateleve', 'idcycle', 'idclasse').filter(
            mateleve__exact=mat)

        # Ici je calcule les effectifs totaux des eleves inscrits
        effectif_total = listeins.count()
        effectif_total_garcons = listeins.filter(mateleve__sexe_eleve='Masculin').count()
        effectif_total_filles = listeins.filter(mateleve__sexe_eleve='Feminin').count()

        pagineinscrit = Paginator(listeins, 10)
        numpageinscrit = request.GET.get('page')
        listeins = pagineinscrit.get_page(numpageinscrit)

    elif (idclass != '' and idclass is not None) and (idcy != '' and idcy is not None) and (
            idansc != '' and idansc is not None):

        listeinsclasse = Inscription.objects.select_related('annee_scolaire', 'mateleve', 'idcycle', 'idclasse').filter(
            Q(idclasse__exact=idclass), Q(idcycle__exact=idcy), Q(annee_scolaire__exact=idansc))

        effectif_total = listeinsclasse.count()
        effectif_total_garcons = listeinsclasse.filter(mateleve__sexe_eleve='Masculin').count()
        effectif_total_filles = listeinsclasse.filter(mateleve__sexe_eleve='Feminin').count()

        pagineinscrit = Paginator(listeinsclasse, 10)
        numpageinscrit = request.GET.get('page')
        listeinsclasse = pagineinscrit.get_page(numpageinscrit)

    elif np != '' and np is not None:
        listeinsnp = Inscription.objects.select_related('annee_scolaire', 'mateleve', 'idcycle', 'idclasse').filter(
            Q(mateleve__nom__icontains=np) | Q(mateleve__prenom__icontains=np))

        effectif_total = listeinsnp.count()
        effectif_total_garcons = listeinsnp.filter(mateleve__sexe_eleve='Masculin').count()
        effectif_total_filles = listeinsnp.filter(mateleve__sexe_eleve='Feminin').count()

        pagineinscrit = Paginator(listeinsnp, 10)
        numpageinscrit = request.GET.get('page')
        listeinsnp = pagineinscrit.get_page(numpageinscrit)

    return render(request, 'gEleve/liste_generale_eleves.html',
                  dict(listeinsmat=listeins, listeinsclasse=listeinsclasse, listenp=listeinsnp,
                       effectif_total=effectif_total, effectif_total_garcons=effectif_total_garcons,
                       effectif_total_filles=effectif_total_filles))


# Gestion de l'impression des recus d'inscription à la scolarité
def recuinscription(request, idinsc):
    # Et là je tente de recuperer les données d'identification de l'école
    ec = Ecole.objects.count()
    if ec == 0:
        messages.error(request, 'Veuillez saisir les informations de l\'école')
    else:
        ecole = Ecole.objects.get(id=1)
        if ecole.logo_ecole:
            data_ecole = [ecole.nom_ecole, ecole.ville_ecole, ecole.prefect_commune,
                          ecole.telephone1, ecole.telephone2, ecole.logo_ecole.path,
                          ecole.devise_ecole, ecole.dsee, ecole.comptable]
        else:
            data_ecole = [ecole.nom_ecole, ecole.ville_ecole, ecole.prefect_commune,
                          ecole.telephone1, ecole.telephone2, 'Logo',
                          ecole.devise_ecole, ecole.dsee, ecole.comptable]

        ins  = Inscription.objects.select_related('annee_scolaire', 'mateleve', 'idcycle', 'idclasse').get(id=idinsc)

        data = [ins.id, ins.annee_scolaire.descript_annee,
                ins.mateleve.matricule, ins.idclasse,
                ins.mateleve.nom, ins.mateleve.prenom,
                ins.mateleve.tuteur, ins.mateleve.contact_pere,
                ins.mateleve.email_pere, ins.date_inscription,
                ins.idclasse.frais_inscription]

        ch  = str(data[1]).split('-')
        ane = ch[1]

        # Numéro de reçu formaté
        numrecu = data[0]
        ansco   = datetime.now().strftime('%y')
        if numrecu < 10:
            numero_recu = ansco + '000' + str(numrecu)
        elif numrecu < 100:
            numero_recu = ansco + '00' + str(numrecu)
        elif numrecu < 1000:
            numero_recu = ansco + '0' + str(numrecu)
        else:
            numero_recu = ansco + str(numrecu)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setTitle('Reçu Inscription Scolarité')

        def draw_entete(y_offset):
            """Dessine l entete complete avec logo et drapeau"""

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
                p.drawString(data_ecole[5],245, 770 + y_offset)

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

        def draw_recu(y_offset):
            """Dessine un exemplaire complet du reçu"""

            draw_entete(y_offset)

            # ── ANNEE SCOLAIRE ET SESSION ──
            p.setFont('Helvetica-Bold', 11)
            p.drawString(150, 700 + y_offset, 'Année Scolaire :')
            p.setFont('Helvetica', 11)
            p.drawString(255, 700 + y_offset, str(data[1]))
            p.setFont('Helvetica-Bold', 11)
            p.drawString(350, 700 + y_offset, 'Session :')
            p.setFont('Helvetica', 11)
            p.drawString(400, 700 + y_offset, str(ane))

            # ── TITRE RECU ──
            p.setFont('Helvetica-Bold', 12)
            p.rect(150, 675 + y_offset, 280, 18, stroke=True, fill=False)
            p.drawString(165, 679 + y_offset, f'RECU INSCRIPTION N° : {numero_recu}')

            # ── INFOS ELEVE GAUCHE ──
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
            p.drawString(120, 600 + y_offset, 'Date inscription :')
            p.setFont('Helvetica', 11)
            p.drawString(220, 600 + y_offset, str(data[9]))

            p.setFont('Helvetica-Bold', 11)
            p.drawString(120, 582 + y_offset, 'Frais inscription :')
            p.setFont('Helvetica', 11)
            p.drawString(220, 582 + y_offset, '{:,} GNF'.format(data[10]))

            p.setFont('Helvetica-Bold', 11)
            p.drawString(120, 564 + y_offset, 'Classe :')
            p.setFont('Helvetica', 11)
            p.drawString(195, 564 + y_offset, str(data[3]))

            # ── INFOS ELEVE DROITE ──
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

            # ── DATE ET SIGNATURE ──
            p.setFont('Helvetica-Bold', 11)
            p.drawString(375, 510 + y_offset, 'Conakry, le ')
            p.drawString(450, 510 + y_offset,
                datetime.now().strftime('%d/%m/%Y'))
            p.drawString(120, 475 + y_offset, 'Le Parent')
            p.drawString(375, 475 + y_offset, 'Le Service Scolarité')
            p.drawString(375, 435 + y_offset, str(data_ecole[8]))

        # ── PREMIER EXEMPLAIRE ──
        draw_recu(0)

        # ── LIGNE SEPARATRICE ──
        p.line(20, 420, 580, 420)

        # ── DEUXIEME EXEMPLAIRE ──
        draw_recu(-420)

        p.showPage()
        p.save()
        buffer.seek(0)

        # ── ENVOI EMAIL ──
        try:
            email = EmailMessage(
                subject='Reçu d\'inscription',
                body=f'Veuillez trouver votre reçu d\'inscription en pièce jointe.\n'
                     f'Cordialement.\nLa Comptabilité : {data_ecole[8]}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[data[8]],
            )
            email.attach(f'Recu_inscription_{str(data[2])}.pdf', buffer.getvalue(), 'application/pdf')
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
        return FileResponse(buffer, as_attachment=False, filename=f'Recu_inscription_{str(data[2])}.pdf', content_type='application/pdf')


# Cette fonction permet d'imprimer les recus d'inscription de manière permanente
def imprimerecuinscription(request, idins):
    return HttpResponseRedirect(reverse('recuinscription',
                                        args=(
                                            idins,)))


# Gestion des reinscription des élèves
def chargeranneecycle(request):
    ans = Inscription.objects.all().distinct('annee_scolaire')
    cy = CycleScolaire.objects.all()
    an = AnneeScolaire.objects.all()
    clas = Classe.objects.all()
    return render(request, 'gEleve/reinscription_eleve.html', dict(ans=ans, cycles=cy, ane=an, clas=clas))


# Cette fonction me permet de charger la liste des élèves inscrits dans une classe donnée aucours d'une année
# scolaire donnée
def chargerlisteeleveclasse(request):
    ane = request.GET.get('anneesco') # anneesco est la valeur renvoyée depuis la fonction JQuery dans le template reinscription_eleve.html
    clas = request.GET.get('id_classe') # id_classe est recupérée depuis la fonction JQuery
    el = Inscription.objects.select_related('annee_scolaire', 'mateleve', 'idcycle', 'idclasse').filter(
        Q(annee_scolaire=ane), Q(idclasse=clas))
    return render(request, 'gEleve/charger_liste_eleve_classe_cycle.html', dict(eleve=el))


# Cette fonction me permet de charger les infos de l'élève sélectionné lors de la reinscription à savoir le prénom, le nom et la photo
def chargerinfoeleveclasse(request):
    matricule = request.GET.get('matricule')
    try:
        el = Eleve.objects.get(matricule=matricule)
        data = {
            'nom': el.nom,
            'prenom': el.prenom,
            'photo': str(el.photo_eleve) if el.photo_eleve else '',
        }
    except Eleve.DoesNotExist:
        data = {'nom': '', 'prenom': '', 'photo': ''}
    
    return JsonResponse(data)


def validerreinscription(request):

    if request.method == 'POST':
        cy = request.POST['cycle']
        ans = request.POST['annee_scolaire_new']
        mat = request.POST['matricule']
        idclas = request.POST['id_classe_new']

        an = AnneeScolaire.objects.get(id=ans)
        cl = Classe.objects.get(id=idclas)
        idcy = CycleScolaire.objects.get(id=cy)
        el = Eleve.objects.get(matricule=mat)

        insc = Inscription(annee_scolaire=an, mateleve=el, idcycle=idcy, idclasse=cl, etat_inscription=ETAT_INSCRIPTION[1][1])
        insc.save()

        frais = Decimal(cl.frais_reinscription)

        # Ici je vais ensuite enregistrer l'état de paiement de la scolarité de l'élève
        eps = EtatPaiementTranche()
        eps.anneescolaire = an
        eps.mateleve = el
        eps.inscription = frais
        eps.idclasse = cl
        eps.save()

        # Je vais enregistrer les frais ainsi validés dans la caisse
        soldecaisse = affichersoldecaisse()
        cais = Caisse()
        cais.type_operation = TYPE_OPERATION_CAISSE_CHOICES[1][1]
        cais.libelle_operation = 'Paiement des frais de reinscription de l\'élève:  {},  {} , {} '.format(
            el.matricule, el.nom, el.prenom)
        cais.montant_encaisse = Decimal(frais)
        cais.anscolaire = an
        cais.categ_depense = CATEGORIE_RECETTE_CHOICES[1][1]
        cais.solde_actuel = Decimal(soldecaisse) + Decimal(frais)
        cais.save()

        # Ici je vais enregistrer l'evenement dans la table Historique
        his = Historique()
        his.nature_operation = 'Reinscription'
        his.detail_operation = 'Reinscription de l\'élève de matricule : {}, {}, {}'.format(
            el.matricule, el.nom, el.prenom)
        his.user_login = 'contact@universtechg'
        his.save()

        messages.success(request, 'Reinscription validée avec succès')

        # Ici je vais recuperer le dernier ID validé de l'Inscription
        idi = Inscription.objects.latest(
            'id')  # Cette instruction permet de recuperer le dernier record suivant l'id
        lastid = idi.id  # Permet de recuperer l'ID de ce dernier record
        return HttpResponseRedirect(reverse('recureinscription',
                                            args=(
                                                lastid,)))  # Je redirige l'utilisateur vers l'impression du recu d'inscription (PDF)
    else:
        return redirect('../listereinscritsanneecourante/')


def recureinscription(request, idinsc):
    
    # Et là je tente de recuperer les données d'identification de l'école    
    ec = Ecole.objects.count()
    if ec == 0:
        messages.error(request, 'Veuillez saisir les informations de l\'école')
    else:
        ecole = Ecole.objects.get(id=1)
        if ecole.logo_ecole:
            data_ecole = [ecole.nom_ecole, ecole.ville_ecole, ecole.prefect_commune,
                          ecole.telephone1, ecole.telephone2, ecole.logo_ecole.path,
                          ecole.devise_ecole, ecole.dsee, ecole.comptable]
        else:
            data_ecole = [ecole.nom_ecole, ecole.ville_ecole, ecole.prefect_commune,
                          ecole.telephone1, ecole.telephone2, 'Logo',
                          ecole.devise_ecole, ecole.dsee, ecole.comptable]

        ins  = Inscription.objects.select_related('annee_scolaire', 'mateleve', 'idcycle', 'idclasse').get(id=idinsc)
        data = [ins.id, ins.annee_scolaire.descript_annee,
                ins.mateleve.matricule, ins.idclasse,
                ins.mateleve.nom, ins.mateleve.prenom,
                ins.mateleve.tuteur, ins.mateleve.contact_pere,
                ins.mateleve.email_pere, ins.date_inscription,
                ins.idclasse.frais_reinscription]

        ch  = str(data[1]).split('-')
        ane = ch[1]

        # Numéro de reçu formaté
        numrecu = data[0]
        ansco   = datetime.now().strftime('%y')
        if numrecu < 10:
            numero_recu = ansco + '000' + str(numrecu)
        elif numrecu < 100:
            numero_recu = ansco + '00' + str(numrecu)
        elif numrecu < 1000:
            numero_recu = ansco + '0' + str(numrecu)
        else:
            numero_recu = ansco + str(numrecu)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setTitle('Reçu Réinscription Scolarité')

        def draw_entete(y_offset):
            """Dessine l entete complete avec logo et drapeau"""

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
                p.drawString(data_ecole[5],245, 770 + y_offset)

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

        def draw_recu(y_offset):
            """Dessine un exemplaire complet du reçu de réinscription"""

            draw_entete(y_offset)

            # ── ANNEE SCOLAIRE ET SESSION ──
            p.setFont('Helvetica-Bold', 11)
            p.drawString(150, 700 + y_offset, 'Année Scolaire :')
            p.setFont('Helvetica', 11)
            p.drawString(255, 700 + y_offset, str(data[1]))
            p.setFont('Helvetica-Bold', 11)
            p.drawString(350, 700 + y_offset, 'Session :')
            p.setFont('Helvetica', 11)
            p.drawString(400, 700 + y_offset, str(ane))

            # ── TITRE RECU ──
            p.setFont('Helvetica-Bold', 12)
            p.rect(150, 675 + y_offset, 280, 18, stroke=True, fill=False)
            p.drawString(155, 679 + y_offset, f'RECU REINSCRIPTION N° : {numero_recu}')

            # ── INFOS ELEVE GAUCHE ──
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
            p.drawString(120, 600 + y_offset, 'Date réinscription :')
            p.setFont('Helvetica', 11)
            p.drawString(230, 600 + y_offset, str(data[9]))

            p.setFont('Helvetica-Bold', 11)
            p.drawString(120, 582 + y_offset, 'Frais réinscription :')
            p.setFont('Helvetica', 11)
            p.drawString(230, 582 + y_offset, '{:,} GNF'.format(data[10]))

            p.setFont('Helvetica-Bold', 11)
            p.drawString(120, 564 + y_offset, 'Classe :')
            p.setFont('Helvetica', 11)
            p.drawString(195, 564 + y_offset, str(data[3]))

            # ── INFOS ELEVE DROITE ──
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

            # ── DATE ET SIGNATURE ──
            p.setFont('Helvetica-Bold', 11)
            p.drawString(375, 510 + y_offset, 'Conakry, le ')
            p.drawString(450, 510 + y_offset,
                datetime.now().strftime('%d/%m/%Y'))
            p.drawString(120, 475 + y_offset, 'Le Parent')
            p.drawString(375, 475 + y_offset, 'Le Service Scolarité')
            p.drawString(375, 435 + y_offset, str(data_ecole[8]))

        # ── PREMIER EXEMPLAIRE ──
        draw_recu(0)

        # ── LIGNE SEPARATRICE ──
        p.line(20, 420, 580, 420)

        # ── DEUXIEME EXEMPLAIRE ──
        draw_recu(-420)

        p.showPage()
        p.save()
        buffer.seek(0)

        # ── ENVOI EMAIL ──
        try:
            email = EmailMessage(
                subject='Reçu de réinscription',
                body=f'Veuillez trouver votre reçu de réinscription en pièce jointe.\n'
                     f'Cordialement.\nLa Comptabilité : {data_ecole[8]}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[data[8]],
            )
            email.attach(f'Recu_reinscription_{str(data[2])}.pdf', buffer.getvalue(), 'application/pdf')
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
        return FileResponse(buffer, as_attachment=False, filename=f'Recu_reinscription_{str(data[2])}.pdf', content_type='application/pdf')


def imprimerecureinscription(request, idins):
    return HttpResponseRedirect(reverse('recureinscription',
                                        args=(
                                            idins,)))

effectif_total = 0
effectif_total_garcons = 0
effectif_total_filles = 0

def listeinscritsanneescolairecourante(request):

    ans = Inscription.objects.all().distinct('annee_scolaire')
    cy = CycleScolaire.objects.all()

    listeeleves = {}
    listeeleves = Inscription.objects.none()

    global effectif_total
    global effectif_total_garcons
    global effectif_total_filles

    mois = date.today()
    mois_actuel = mois.strftime('%m')

    listeeleves = Inscription.objects.select_related('annee_scolaire', 'mateleve', 'idcycle', 'idclasse').filter(
            Q(etat_inscription__exact=ETAT_INSCRIPTION[0][1]),Q(date_inscription__month=mois_actuel)).order_by('-date_inscription')
    
    effectif_total = listeeleves.count()
    effectif_total_garcons = listeeleves.filter(mateleve__sexe_eleve=SEXE_ELEVE_CHOICES[1][1]).count() # SEXE_ELEVE_CHOICES[1][1] correspond à Masculin
    effectif_total_filles = listeeleves.filter(mateleve__sexe_eleve=SEXE_ELEVE_CHOICES[2][1]).count() # SEXE_ELEVE_CHOICES[2][1] correspond à Feminin
    
    pagineins = Paginator(listeeleves, 10)
    numpageins = request.GET.get('page')
    listeeleves = pagineins.get_page(numpageins)
    
    return render(request, 'gEleve/liste_eleves_inscrits.html', dict(ans=ans, cycles=cy, listeeleves=listeeleves, effectif_total=effectif_total, effectif_total_garcons=effectif_total_garcons, effectif_total_filles=effectif_total_filles))


def listereinscritsanneescolairecourante(request):

    ans = Inscription.objects.all().distinct('annee_scolaire')
    cy = CycleScolaire.objects.all()

    listeeleves = {}
    listeeleves = Inscription.objects.none()

    global effectif_total
    global effectif_total_garcons
    global effectif_total_filles

    mois = date.today()
    mois_actuel = mois.strftime('%m')

    listeeleves = Inscription.objects.select_related('annee_scolaire', 'mateleve', 'idcycle', 'idclasse').filter(
            Q(etat_inscription__exact=ETAT_INSCRIPTION[1][1]),Q(date_inscription__month=mois_actuel)).order_by('-date_inscription')
    
    effectif_total = listeeleves.count()
    effectif_total_garcons = listeeleves.filter(mateleve__sexe_eleve=SEXE_ELEVE_CHOICES[1][1]).count() # SEXE_ELEVE_CHOICES[1][1] correspond à Masculin
    effectif_total_filles = listeeleves.filter(mateleve__sexe_eleve=SEXE_ELEVE_CHOICES[2][1]).count() # SEXE_ELEVE_CHOICES[2][1] correspond à Feminin
    
    pagineins = Paginator(listeeleves, 10)
    numpageins = request.GET.get('page')
    listeeleves = pagineins.get_page(numpageins)
    
    return render(request, 'gEleve/liste_eleves_reinscrits.html', dict(ans=ans, cycles=cy, listeeleves=listeeleves, effectif_total=effectif_total, effectif_total_garcons=effectif_total_garcons, effectif_total_filles=effectif_total_filles))


def filtrelisteinscrits(request):
    
    idclass = request.GET.get('id_classe')
    idcy = request.GET.get('cycle')
    idansc = request.GET.get('annee_scolaire')

    listeinsclasse = {}
    listeinsclasse = Inscription.objects.none()

    global effectif_total
    global effectif_total_garcons
    global effectif_total_filles

    if (idclass != '' and idclass is not None) and (idcy != '' and idcy is not None) and (
            idansc != '' and idansc is not None):
        listeinsclasse = Inscription.objects.select_related('annee_scolaire', 'mateleve', 'idcycle', 'idclasse').filter(
            Q(idclasse__exact=idclass), Q(idcycle__exact=idcy), Q(annee_scolaire__exact=idansc), Q(etat_inscription__exact=ETAT_INSCRIPTION[0][1])).order_by('-date_inscription')


        # Ici je calcule les effectifs totaux des eleves inscrits
        effectif_total = listeinsclasse.count()
        effectif_total_garcons = listeinsclasse.filter(mateleve__sexe_eleve=SEXE_ELEVE_CHOICES[1][1]).count() # SEXE_ELEVE_CHOICES[1][1] correspond à Masculin
        effectif_total_filles = listeinsclasse.filter(mateleve__sexe_eleve=SEXE_ELEVE_CHOICES[2][1]).count() # SEXE_ELEVE_CHOICES[2][1] correspond à Feminin

        pagineinscrit = Paginator(listeinsclasse, 10)
        numpageinscrit = request.GET.get('page')
        listeinsclasse = pagineinscrit.get_page(numpageinscrit)
        
    return render(request, 'gEleve/liste_eleves_inscrits.html',
                  dict(listeinscrits=listeinsclasse, effectif_total=effectif_total,
                       effectif_total_garcons=effectif_total_garcons, effectif_total_filles=effectif_total_filles))


def filtrelistereinscrits(request):
    
    idclass = request.GET.get('id_classe')
    idcy = request.GET.get('cycle')
    idansc = request.GET.get('annee_scolaire')

    listeinsclasse = {}
    listeinsclasse = Inscription.objects.none()

    global effectif_total
    global effectif_total_garcons
    global effectif_total_filles

    if (idclass != '' and idclass is not None) and (idcy != '' and idcy is not None) and (
            idansc != '' and idansc is not None):
        listeinsclasse = Inscription.objects.select_related('annee_scolaire', 'mateleve', 'idcycle', 'idclasse').filter(
            Q(idclasse__exact=idclass), Q(idcycle__exact=idcy), Q(annee_scolaire__exact=idansc), Q(etat_inscription__exact=ETAT_INSCRIPTION[1][1])).order_by('-date_inscription')


        # Ici je calcule les effectifs totaux des eleves inscrits
        effectif_total = listeinsclasse.count()
        effectif_total_garcons = listeinsclasse.filter(mateleve__sexe_eleve=SEXE_ELEVE_CHOICES[1][1]).count() # SEXE_ELEVE_CHOICES[1][1] correspond à Masculin
        effectif_total_filles = listeinsclasse.filter(mateleve__sexe_eleve=SEXE_ELEVE_CHOICES[2][1]).count() # SEXE_ELEVE_CHOICES[2][1] correspond à Feminin

        pagineinscrit = Paginator(listeinsclasse, 10)
        numpageinscrit = request.GET.get('page')
        listeinsclasse = pagineinscrit.get_page(numpageinscrit)
        
    return render(request, 'gEleve/liste_eleves_reinscrits.html',
                  dict(listereinscrits=listeinsclasse, effectif_total=effectif_total,
                       effectif_total_garcons=effectif_total_garcons, effectif_total_filles=effectif_total_filles))
