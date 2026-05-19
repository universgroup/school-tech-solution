from decimal import Decimal

from .forms import *
from .models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator  # Utilisé dans la gestion des paginations des différentes listes de données
from django.utils.datastructures import MultiValueDictKeyError
from random import randrange  # Utilisé dans la generation des matricules des élèves
from datetime import datetime  # Utilisé pour recuperer l'année courante dans la generation des matricules des élèves
from django.db.models import Q  # Permet de faire des requêtes avec les opérateurs And (,) et les opérateurs OR (|)
import io  # Librairie contenant les methodes utilisant les péripheriques d'entrées/sorties
from django.http import FileResponse, HttpResponseRedirect
from reportlab.pdfgen import canvas
from reportlab.platypus.tables import Table, TableStyle  # Permet de generer des tableaux (matrices) de données
from reportlab.lib import colors  # Contient les méthodes/fonctions de gestion des couleurs
from django.urls import reverse
from django.db.models import Sum  # Permet d'effectuer la requete avec la fonction aggregée Sum



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
    return render(request, 'enregistrer_matiere.html', {'form': formmatiere})


def listematiere(request):
    mat = Matiere.objects.all().order_by('nom_matiere')
    paginemat = Paginator(mat, 10)  # Permet de définir une pagination sur 10 lignes/enregistrements
    num_pagemat = request.GET.get('page')  # Permet de recuperer le numéro de page selectionné
    mat = paginemat.get_page(num_pagemat)  # J'affiche la page correspondant au numéro selectionné
    context = {'mat': mat}
    return render(request, 'liste_matiere.html', context)


def editermatiere(request, idmat):
    mat = Matiere.objects.get(id=idmat)
    context = {'mat': mat}
    return render(request, 'modifier_matiere.html', context)


def detailsmatiere(request, codemat):
    mat = Matiere.objects.get(id=codemat)
    return render(request, 'afficher_details_matiere.html', dict(mat=mat))


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



# Gestion du personnel

def ajouterpersonnel(request):
    if request.method == 'POST':
        formpersonnel = FormPersonnel(request.POST)
        if formpersonnel.is_valid():
            formpersonnel.save()
            formpersonnel = FormPersonnel()
            messages.success(request, 'Employé enregistré avec succès')
    else:
        formpersonnel = FormPersonnel()
    context = {'form': formpersonnel}
    return render(request, 'enregistrer_personnel.html', context)


def listepersonnel(request):
    pers = Personnel.objects.all().order_by('nom_personnel')
    paginepers = Paginator(pers, 10)
    numpagepers = request.GET.get('page')
    pers = paginepers.get_page(numpagepers)
    return render(request, 'liste_generale_personnel.html', dict(pers=pers))


def editerpersonnel(request, idpers):
    pers = Personnel.objects.get(id=idpers)
    context = {'pers': pers}
    return render(request, 'modifier_personnel.html', context)


def detailspersonnel(request, idpers):
    pers = Personnel.objects.get(id=idpers)
    return render(request, 'afficher_details_personnel.html', dict(pers=pers))


def modifierpersonnel(request, idpers):
    if request.method == 'POST':
        pers = Personnel.objects.get(id=idpers)
        pers.nom_personnel = request.POST['nom_personnel']
        pers.prenom_personnel = request.POST['prenom_personnel']
        pers.civilite = request.POST['civilite']
        pers.date_naissance = request.POST['date_naissance']
        pers.niveau_etude = request.POST['niveau_etude']
        pers.type_personnel = request.POST['type_personnel']
        pers.adresse_personnel = request.POST['adresse_personnel']
        pers.contact_personnel = request.POST['contact_personnel']
        pers.fonction_personnel = request.POST['fonction_personnel']
        pers.email_personnel = request.POST['email_personnel']
        pers.sexe_personnel = request.POST['sexe_personnel']
        pers.salbase = request.POST['salbase']
        pers.annee_experience = request.POST['annee_experience']
        pers.contrat_type = request.POST['type_contrat']
        pers.diplome = request.POST['diplome']
        pers.date_embauche = request.POST['date_embauche']
        pers.save()
        return redirect('/listegeneralepersonnel/')
    else:
        return redirect('/listegeneralepersonnel/')


def supprimerpersonnel(request, pk):
    pers = Personnel.objects.get(id=pk)
    pers.delete()
    messages.success(request, 'Employé supprimé avec succès')
    return redirect('/ajouterpersonnel/')


# Gestion des Salaires
def enregistrersalaire(request):
    if request.method == 'POST':
        formsalaire = FormSalaire(request.POST)
        if formsalaire.is_valid():
            ansc = request.POST.get('anneescolaire')
            ans = AnneeScolaire.objects.get(id=ansc)
            idper = request.POST.get('idpersonnel')
            idp = Personnel.objects.get(id=idper)
            typers = idp.type_personnel

            # Je tente de recuperer ici le montant des avances sur salaire de l'employé selectionné
            mavce = AvanceSalaire.objects.filter(idpersonnel=idp).aggregate(tavance=Sum('montant_avance'))
            total_avance = mavce['tavance']

            sal = Salaire()
            sal.mois_paie = request.POST['mois_paie']
            sal.detail_paiement = request.POST['detail_paiement']
            nbheure = request.POST['nbre_heure']
            thoraire = request.POST['taux_horaire']
            sal.anneescolaire = ans
            sal.idpersonnel = idp
            sal.avance_paie = Decimal(total_avance)
            sal.primes = request.POST['primes']
            sal.nb_hsupp = request.POST['nb_hsupp']
            sal.mont_hsupp = request.POST['mont_hsupp']

            salb = 0
            if typers == TYPE_PERSONNEL[2][1]:  # TYPE_PERSONNEL[2][1] == 'Permanent'
                salb = Decimal(idp.salbase)
            elif typers == TYPE_PERSONNEL[1][1]:  # TYPE_PERSONNEL[2][1] == 'Vacataire'
                sal.nbre_heure = int(nbheure)
                sal.taux_horaire = Decimal(thoraire)
                salb = Decimal(thoraire) * Decimal(nbheure)

            sb = salb + Decimal(sal.primes) + Decimal(sal.mont_hsupp)
            sal.salbrut = sb
            # cotis = Decimal(0.05) * sb
            cotis = 0
            sal.cotis_sociale = cotis
            snet = sb - Decimal(total_avance) - cotis
            sal.salnet = snet

            # Enregistrement du salaire dans la caisse
            soldec = affichersoldecaisse()
            if soldec > snet:
                sal.save()

                cais = Caisse()
                cais.anscolaire = ans
                cais.libelle_operation = 'Paiement du salaire de l\'employé {} {} {} au compte du mois de {}'.format(
                    idp.id, idp.nom_personnel, idp.prenom_personnel, sal.mois_paie)
                cais.montant_encaisse = sal.salnet
                cais.type_operation = TYPE_OPERATION_CAISSE_CHOICES[2][1]
                cais.solde_actuel = soldec - sal.salnet
                cais.categ_depense = CATEGORIE_DEPENSE_CHOICES[1][1]
                cais.save()
                messages.success(request, 'Salaire enregistré avec succès')

                # Ici je vais enregistrer l'evenement dans la table Historique
                his = Historique()
                his.nature_operation = CATEGORIE_DEPENSE_CHOICES[1][1]
                his.detail_operation = 'Paiement du salaire de l\'employé : {}, {}, {}, pour le mois de {}'.format(
                    sal.idpersonnel.id, idp.nom_personnel, idp.prenom_personnel, sal.mois_paie)
                his.user_login = 'contact@universtechg'
                his.save()

                # Ici je vais recuperer le dernier ID salaire en vue de pouvoir imprimer le bulletin de salaire
                idsal = Salaire.objects.latest('id')

                lastid = idsal.id  # Permet de recuperer l'ID de ce dernier record
                return HttpResponseRedirect(reverse('recubulletinsalaire',
                                                    args=(
                                                        lastid,)))

            else:
                messages.error(request, 'Impossible de valider cette opération car le solde caisse est insuffisant')
    else:
        formsalaire = FormSalaire()

    salaire = Salaire.objects.select_related('anneescolaire', 'idpersonnel').all().order_by('idpersonnel')
    mont_base = Personnel.objects.all().aggregate(tbase=Sum('salbase'))
    mont_primes = Salaire.objects.select_related('anneescolaire', 'idpersonnel').all().aggregate(tprimes=Sum('primes'))
    mont_brut = Salaire.objects.select_related('anneescolaire', 'idpersonnel').all().aggregate(tbrut=Sum('salbrut'))
    mont_avance = Salaire.objects.select_related('anneescolaire', 'idpersonnel').all().aggregate(
        tavances=Sum('avance_paie'))
    mont_net = Salaire.objects.select_related('anneescolaire', 'idpersonnel').all().aggregate(
        tnet=Sum('salnet'))

    total_salbase = mont_base['tbase']
    total_primes = mont_primes['tprimes']
    total_salbrut = mont_brut['tbrut']
    total_avance = mont_avance['tavances']
    total_salnet = mont_net['tnet']

    soldec = affichersoldecaisse()  # Je recupère le dernier solde caisse après l'opération

    paginesalaire = Paginator(salaire, 10)
    numpagesalaire = request.GET.get('page')
    salaire = paginesalaire.get_page(numpagesalaire)
    context = {'form': formsalaire, 'sal': salaire, 'total_salbase': total_salbase, 'total_primes': total_primes,
               'total_salbrut': total_salbrut, 'total_avance': total_avance, 'total_salnet': total_salnet,
               'soldec': soldec}
    return render(request, 'enregistrer_salaire.html', context)


def editersalaire(request, idsal):
    sal = Salaire.objects.get(id=idsal)
    context = {'sal': sal}
    return render(request, 'modifier_salaire.html', context)


def detailssalaire(request, idsal):
    sal = Salaire.objects.get(id=idsal)
    return render(request, 'afficher_details_salaire.html', dict(sal=sal))


def modifiersalaire(request, idsal):
    if request.method == 'POST':
        sal = Salaire.objects.get(id=idsal)
        sal.nbre_heure = request.POST['nbre_heure']
        sal.mois_paie = request.POST['mois_paie']
        sal.detail_paiement = request.POST['detail_paiement']
        sal.taux_horaire = request.POST['taux_horaire']
        sal.avance_paie = request.POST['avance_paie']
        sal.primes = request.POST['primes']
        sal.nb_hsupp = request.POST['nb_hsupp']
        sal.mont_hsupp = request.POST['mont_hsupp']

        sal.save()
        return redirect('/ajoutersalaire/')
    else:
        return redirect('/ajoutersalaire/')


def supprimersalaire(request, pk):
    sal = Salaire.objects.get(id=pk)
    sal.delete()
    messages.success(request, 'Ligne de salaire supprimée avec succès')
    return redirect('/ajoutersalaire/')


# Gestion des Avances sur Salaire

def ajouteravancesalaire(request):
    if request.method == 'POST':
        formavancesalaire = FormAvanceSalaire(request.POST)
        if formavancesalaire.is_valid():
            idpers = request.POST.get('idpersonnel')
            ans = request.POST.get('anscolaire')
            idp = Personnel.objects.get(id=idpers)
            anc = AnneeScolaire.objects.get(id=ans)

            avc = AvanceSalaire()
            avc.mois_avance = request.POST['mois_avance']
            avc.intitule = request.POST['intitule']
            mont_avce = Decimal(request.POST['montant_avance'])
            avc.montant_avance = mont_avce
            avc.anscolaire = anc
            avc.idpersonnel = idp

            soldec = affichersoldecaisse()
            if soldec > mont_avce:
                avc.save()

                cais = Caisse()
                cais.anscolaire = anc
                cais.libelle_operation = 'Paiement avance sur salaire de l\'employé {} {} {}, pour le mois de {}'.format(
                    avc.idpersonnel.id, idp.nom_personnel, idp.prenom_personnel, avc.mois_avance)
                cais.montant_encaisse = mont_avce
                cais.solde_actuel = soldec - mont_avce
                cais.categ_depense = CATEGORIE_DEPENSE_CHOICES[1][1]
                cais.type_operation = TYPE_OPERATION_CAISSE_CHOICES[2][1]
                cais.save()

                # Ici je vais enregistrer l'evenement dans la table Historique
                his = Historique()
                his.nature_operation = 'Avance sur salaire'
                his.detail_operation = 'Paiement de l\'avance sur salaire de l\'employé : {}, {}, {}, pour le mois de {}'.format(
                    avc.idpersonnel.id, idp.nom_personnel, idp.prenom_personnel, avc.mois_avance)
                his.user_login = 'contact@universtechg'
                his.save()

                messages.success(request, 'Avance sur salaire validée avec succès')

                # Ici je vais recuperer le dernier ID avance salaire en vue de pouvoir imprimer le recu d'avance sur salaire
                idavce = AvanceSalaire.objects.latest('id')

                lastid = idavce.id  # Permet de recuperer l'ID de ce dernier record
                return HttpResponseRedirect(reverse('recuavancesalaire',
                                                    args=(
                                                        lastid,)))
            else:
                messages.error(request, 'Impossible de valider cette opération car le solde caisse est insuffisant')
    else:
        formavancesalaire = FormAvanceSalaire()
    avsal = AvanceSalaire.objects.select_related('idpersonnel', 'anscolaire').all().order_by('-date_avance')
    mont_total = AvanceSalaire.objects.all().aggregate(montavance=Sum('montant_avance'))
    total_avance = mont_total['montavance']

    soldec = affichersoldecaisse()  # Je recupère le dernier solde caisse après l'opération

    pagineavance = Paginator(avsal, 10)
    numpageavance = request.GET.get('page')
    avsal = pagineavance.get_page(numpageavance)
    context = {'form': formavancesalaire, 'avsal': avsal, 'total_avance': total_avance, 'soldec': soldec}
    return render(request, 'enregistrer_avance_salaire.html', context)


def editeravancesalaire(request, idavsal):
    avsal = AvanceSalaire.objects.get(id=idavsal)
    context = {'avsal': avsal}
    return render(request, 'modifier_avance_salaire.html', context)


def detailsavancesalaire(request, idavsal):
    avsal = AvanceSalaire.objects.get(id=idavsal)
    return render(request, 'afficher_details_avance_salaire.html', dict(avsal=avsal))


def modifieravancesalaire(request, idavsal):
    if request.method == 'POST':
        avsal = AvanceSalaire.objects.get(id=idavsal)
        avsal.montant_avance = request.POST['montant_avance']
        avsal.intitule = request.POST['intitule']
        avsal.mois_avance = request.POST['mois_avance']
        avsal.save()
        return redirect('/ajouteravancesalaire/')
    else:
        return redirect('/ajouteravancesalaire/')


def supprimeravancesalaire(request, pk):
    avsal = AvanceSalaire.objects.get(id=pk)
    avsal.delete()
    messages.success(request, 'Avance sur salaire supprimées')
    return redirect('/ajouteravancesalaire/')


# Impression du bon d'avance sur salaire
def recubonavancesalaire(request, idavance):
    # Et là je tente de recuperer les données d'identification de l'école
    ecole = Ecole.objects.get(id=1)
    if ecole.logo_ecole:
        data_ecole = [ecole.nom_ecole, ecole.ville_ecole, ecole.prefect_commune, ecole.telephone1, ecole.telephone2,
                      ecole.logo_ecole, ecole.devise_ecole, ecole.dsee, ecole.comptable]
    else:
        data_ecole = [ecole.nom_ecole, ecole.ville_ecole, ecole.prefect_commune, ecole.telephone1, ecole.telephone2,
                      'Logo', ecole.devise_ecole, ecole.dsee, ecole.comptable]

    # Ici je tente de recuperer les données sur l'avance de salaire depuis la BD

    avce = AvanceSalaire.objects.select_related('idpersonnel', 'anscolaire').get(id=idavance)
    data = [avce.id, avce.anscolaire.descript_annee, avce.idpersonnel.id, avce.idpersonnel.nom_personnel,
            avce.idpersonnel.prenom_personnel, avce.idpersonnel.fonction_personnel, avce.idpersonnel.contact_personnel,
            avce.mois_avance]

    mont_avance = '{:,} GNF'.format(avce.montant_avance)  # Je formate le montant avancé en monétaire
    table_data = [['Description', 'Montant avancé', 'Date'], [avce.intitule, mont_avance, avce.date_avance]]

    ch = str(data[1])  # Je recupère le nom de l'année scolaire i.e 2023-2024 par exemple
    ch = ch.split('-')  # Je découpe la chaine obtenue en deux sous chaines tenant compte du séparateur (-)
    ane = ch[1]  # Je recupère la deuxième sous chaine i.e 2024 par exemple

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    p.setTitle('Reçu Avance sur Salaire')  # Permet de définir le Titre du Document

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    # Ecriture des textes de l'entête superieur gauche
    p.setFontSize(10)
    p.drawString(20, 815, 'MEPU-A')
    p.drawString(20, 798, 'IRE : ')
    p.drawString(55, 798, str(data_ecole[1]))
    p.drawString(20, 785, 'DCE : ')
    p.drawString(55, 785, str(data_ecole[2]))
    p.drawString(20, 770, 'DSEE :')
    p.drawString(55, 770, str(data_ecole[7]))
    p.drawString(20, 755, 'TEL : ')
    p.drawString(55, 755, str(data_ecole[3]) + ' / ' + str(data_ecole[4]))

    # Affichage du logo de l'ecole et le drapeau de la République
    try:
        p.drawImage(str(data_ecole[5]), 235, 815, 100, 100)
    except FileNotFoundError:
        pass
    except OSError:
        pass

    p.setFillColor("Red")  # Définit la couleur de remplissage du 1er rectangle à Rouge
    p.rect(449, 815, 30, 10, stroke=False,
           fill=True)  # fill = True permet de définir la couleur de remplissage du 1er rectangle
    p.setFillColor("yellow")
    p.rect(479, 815, 30, 10, stroke=False, fill=True)
    p.setFillColor("green")
    p.rect(509, 815, 30, 10, stroke=False, fill=True)

    p.setFillColor("black")  # Définit la couleur de police (black) pour le reste du document
    # Ecriture des textes de l'entête supérieur droit
    p.setFontSize(10)
    p.drawString(450, 798, 'République de Guinée')

    # p.setFontSize(9)
    p.setFont('Helvetica-Oblique', 9)
    p.drawString(450, 780, 'Travail-Justice-Solidarité')

    p.setFont('Helvetica', 11)
    p.drawString(225, 740, str(data_ecole[0]))  # Nom de l'école

    p.setFont('Helvetica-Oblique', 9)
    p.drawString(225, 720, str(data_ecole[6]))  # Devise de l'école

    # Tracé de ligne séparatrice entre l'entête et le reste du document
    p.line(140, 710, 440, 710)

    p.setFont('Helvetica', 11)
    # Ecriture de la deuxième partie de l'entête
    p.drawString(150, 695, 'Année Scolaire :')
    p.drawString(245, 695, str(data[1]))
    p.drawString(330, 695, 'Session : ')
    p.drawString(385, 695, str(ane))
    p.drawString(180, 673, 'RECU AVANCE/SALAIRE N° : ')

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

    p.drawString(335, 673, str(numero_recu))

    num_emp = data[2]  # Ici je recupère l'ID de l'employé depuis la liste ci-haut
    id_emp = ''

    if num_emp < 10:
        id_emp = ansco + '00' + str(num_emp)
    elif num_emp < 100:
        id_emp = ansco + '0' + str(num_emp)
    elif num_emp < 1000:
        id_emp = ansco + '0' + str(num_emp)
    elif num_emp < 10000:
        id_emp = ansco + '0' + str(num_emp)

    # Ecriture des informations de l'élève
    p.drawString(120, 645, 'ID Employé : ')
    p.drawString(185, 645, str(id_emp))
    p.drawString(120, 629, 'Nom : ')
    p.drawString(185, 629, str(data[3]))
    p.drawString(120, 610, 'Prénoms : ')
    p.drawString(185, 610, str(data[4]))
    p.drawString(120, 590, 'Fonction : ')
    p.drawString(185, 590, str(data[5]))

    # Informations placées à droite dans la rubrique des informations de l'élève
    p.drawString(315, 629, 'Contact : ')
    p.drawString(365, 629, str(data[6]))
    p.drawString(315, 610, 'Mois de : ')
    p.drawString(365, 610, str(data[7]).upper())

    # Insertion du tableau des deonnées contenant la description de l'opération, le montant avancé et la date de l'opération
    table = Table(
        table_data)  # Permet de créer un tableau à deux (2) dimensions contenant les données stockées dans "table_data" declaré plus haut
    table.wrapOn(p, 400, 100)  # Je définis la largeur et la hauteur du tableau dans le canvas

    # Je procède ici à la mise en forme du tableau
    table.setStyle(TableStyle([  # Mise en forme de l'entête du tableau des données
        ('VALIGN', (0, 0), (2, 0), 'MIDDLE'),  # Alignement vertical du texte de l'entête
        ('TEXTCOLOR', (0, 0), (2, 0), colors.black),  # Couleur de texte de l'entête
        ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),  # Style de police de l'entête
        ('FONTSIZE', (0, 0), (2, 0), 10),  # Taille de police de l'entête
        ('ALIGN', (0, 0), (2, 0), 'LEFT'),  # Alignement horizontal de l'entête

        # Mise en forme du corps du tableau
        ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),  # Alignement vertical du contenu du tableau
        ('ALIGN', (0, -1), (-1, -1), 'LEFT'),  # Alignement horizontal du contenu du tableau
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),  # Couleur de texte du contenu
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica'),  # Style de police du contenu
        ('FONTSIZE', (0, -1), (-1, -1), 10),  # Taille de police du contenu

        # Bordures internes et externes
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),  # Couleur, épaisseur des bordures internes
        ('BOX', (0, 0), (-1, -1), 1, colors.black),  # Couleur, épaisseur des bordures externes

    ]))

    table.drawOn(p, 115, 535)  # Je dessine le tableau dans le canvas selon les coordonnées indiquées

    # Ecriture des informations du bas de la page, Date d'impression, signature du DG et de la partie reservée au parent d'élève
    p.drawString(375, 485, 'Conakry, le ')
    p.drawString(440, 485, datetime.now().strftime('%d/%m/%Y'))
    p.drawString(120, 440, 'Le Bénéficiaire')
    p.drawString(375, 440, 'La Comptabilité')
    p.drawString(375, 385, str(data_ecole[8]))

    # J'insere ici une ligne séparatrice pour diviser le reçu en deux (2) copies
    p.line(20, 370, 580, 370)

    # Ici commence la deuxième partie du reçu

    p.setFont('Helvetica', 11)
    # Ecriture de la deuxième partie de l'entête
    p.drawString(150, 345, 'Année Scolaire :')
    p.drawString(245, 345, str(data[1]))
    p.drawString(330, 345, 'Session : ')
    p.drawString(385, 345, str(ane))
    p.drawString(180, 323, 'RECU AVANCE/SALAIRE N° : ')
    p.drawString(335, 323, str(numero_recu))

    # Ecriture des informations de l'élève
    p.drawString(120, 295, 'ID Employé : ')
    p.drawString(185, 295, str(id_emp))
    p.drawString(120, 279, 'Nom : ')
    p.drawString(185, 279, str(data[3]))
    p.drawString(120, 260, 'Prénoms : ')
    p.drawString(185, 260, str(data[4]))
    p.drawString(120, 240, 'Fonction : ')
    p.drawString(185, 240, str(data[5]))
    # Informations placées à droite dans la rubrique des informations de l'élève
    p.drawString(315, 279, 'Contact : ')
    p.drawString(365, 279, str(data[6]))
    p.drawString(315, 260, 'Mois de : ')
    p.drawString(365, 260, str(data[7]).upper())

    table.drawOn(p, 115, 185)  # Je dessine le tableau dans le canvas selon les coordonnées indiquées

    # Ecriture des informations du bas de la page, Date d'impression, signature du DG et de la partie reservée au parent d'élève
    p.drawString(375, 125, 'Conakry, le ')
    p.drawString(440, 125, datetime.now().strftime('%d/%m/%Y'))
    p.drawString(120, 80, 'Le Bénéficiaire')
    p.drawString(375, 80, 'La Comptabilité')
    p.drawString(375, 25, str(data_ecole[8]))

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename='Bon_Avance_Salaire ' + str(id_emp) + '.pdf',
                        content_type='application/pdf')


def recubulletinsalaire(request, idsal):
    # Et là je tente de recuperer les données d'identification de l'école
    ecole = Ecole.objects.get(id=1)
    if ecole.logo_ecole:
        data_ecole = [ecole.nom_ecole, ecole.ville_ecole, ecole.prefect_commune, ecole.telephone1, ecole.telephone2,
                      ecole.logo_ecole, ecole.devise_ecole, ecole.dsee, ecole.comptable]
    else:
        data_ecole = [ecole.nom_ecole, ecole.ville_ecole, ecole.prefect_commune, ecole.telephone1, ecole.telephone2,
                      'Logo', ecole.devise_ecole, ecole.dsee, ecole.comptable]

    # Ici je tente de recuperer les données sur le salaire de l'employe depuis la BD

    sal = Salaire.objects.select_related('idpersonnel', 'anneescolaire').get(id=idsal)

    data = [sal.anneescolaire.descript_annee, sal.mois_paie]

    num_emp = sal.idpersonnel.id  # Ici je recupère l'ID de l'employé depuis la liste ci-haut
    id_emp = ''
    ansco = datetime.now().strftime('%y')  # Je recupère uniquement l'année de la date courante

    if num_emp < 10:
        id_emp = ansco + '00' + str(num_emp)
    elif num_emp < 100:
        id_emp = ansco + '0' + str(num_emp)
    elif num_emp < 1000:
        id_emp = ansco + '0' + str(num_emp)
    elif num_emp < 10000:
        id_emp = ansco + '0' + str(num_emp)

    table_data_info = [['ID Employé', id_emp], ['Nom', sal.idpersonnel.nom_personnel],
                       ['Prénoms', sal.idpersonnel.prenom_personnel], ['Contact', sal.idpersonnel.contact_personnel],
                       ['Fonction', sal.idpersonnel.fonction_personnel]]

    # Permet de formater en monétaire tous les montants
    th = '{:,} GNF'.format(sal.taux_horaire)
    sbase = '{:,} GNF'.format(sal.idpersonnel.salbase)
    primes = '{:,} GNF'.format(sal.primes)
    sbrut = '{:,} GNF'.format(sal.salbrut)
    mavance = '{:,} GNF'.format(sal.avance_paie)
    cotis = '{:,} GNF'.format(sal.cotis_sociale)
    snet = '{:,} GNF'.format(sal.salnet)

    table_data_salaire = [['Détails', sal.detail_paiement], ['NB heure', sal.nbre_heure], ['Taux horaire', th],
                          ['Salaire base', sbase], ['Montant primes', primes], ['Heure supp', sal.nb_hsupp],
                          ['Salaire brut', sbrut], ['Montant avancé', mavance], ['Cotisation sociale', cotis],
                          ['Salaire net', snet]]

    ch = str(data[0])  # Je recupère le nom de l'année scolaire i.e 2023-2024 par exemple
    ch = ch.split('-')  # Je découpe la chaine obtenue en deux sous chaines tenant compte du séparateur (-)
    ane = ch[1]  # Je recupère la deuxième sous chaine i.e 2024 par exemple

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    p.setTitle('Bulletin de Salaire')  # Permet de définir le Titre du Document

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    # Ecriture des textes de l'entête superieur gauche
    p.setFontSize(10)
    p.drawString(20, 815, 'MEPU-A')
    p.drawString(20, 798, 'IRE : ')
    p.drawString(55, 798, str(data_ecole[1]))
    p.drawString(20, 785, 'DCE : ')
    p.drawString(55, 785, str(data_ecole[2]))
    p.drawString(20, 770, 'DSEE :')
    p.drawString(55, 770, str(data_ecole[7]))
    p.drawString(20, 755, 'TEL : ')
    p.drawString(55, 755, str(data_ecole[3]) + ' / ' + str(data_ecole[4]))

    # Affichage du logo de l'ecole et le drapeau de la République
    try:
        p.drawImage(str(data_ecole[5]), 235, 815, 100, 100)
    except FileNotFoundError:
        pass
    except OSError:
        pass

    p.setFillColor("Red")  # Définit la couleur de remplissage du 1er rectangle à Rouge
    p.rect(449, 815, 30, 10, stroke=False,
           fill=True)  # fill = True permet de définir la couleur de remplissage du 1er rectangle
    p.setFillColor("yellow")
    p.rect(479, 815, 30, 10, stroke=False, fill=True)
    p.setFillColor("green")
    p.rect(509, 815, 30, 10, stroke=False, fill=True)

    p.setFillColor("black")  # Définit la couleur de police (black) pour le reste du document
    # Ecriture des textes de l'entête supérieur droit
    p.setFontSize(10)
    p.drawString(450, 798, 'République de Guinée')

    # p.setFontSize(9)
    p.setFont('Helvetica-Oblique', 9)
    p.drawString(450, 780, 'Travail-Justice-Solidarité')

    p.setFont('Helvetica', 11)
    p.drawString(225, 740, str(data_ecole[0]))  # Nom de l'école

    p.setFont('Helvetica-Oblique', 9)
    p.drawString(225, 720, str(data_ecole[6]))  # Devise de l'école

    # Tracé de ligne séparatrice entre l'entête et le reste du document
    p.line(140, 710, 440, 710)

    p.setFont('Helvetica', 11)
    # Ecriture de la deuxième partie de l'entête
    p.drawString(150, 695, 'Année Scolaire :')
    p.drawString(245, 695, str(data[0]))
    p.drawString(330, 695, 'Session : ')
    p.drawString(385, 695, str(ane))
    p.setFont('Helvetica-Bold', 12)
    p.drawString(180, 665, 'BULLETIN DE PAIE DU MOIS DE : ')
    p.drawString(377, 665, str(data[1]).upper())

    # Ecriture du titre du tableau de données 1
    p.drawString(150, 635, 'INFORMATIONS PERSONNELLES')
    p.setFont('Helvetica', 11)

    # Insertion du tableau des données contenant les informations personnelles liées à l'employé
    table_perso = Table(
        table_data_info)  # Permet de créer un tableau à deux (2) dimensions contenant les données stockées dans "table_data_info" declaré plus haut
    table_perso.wrapOn(p, 400, 100)  # Je définis la largeur et la hauteur du tableau dans le canvas

    # Je procède ici à la mise en forme du tableau
    table_perso.setStyle(TableStyle([  # Mise en forme de l'entête du tableau des données
        ('VALIGN', (0, 0), (-2, -1), 'MIDDLE'),  # Alignement vertical du texte de l'entête
        ('TEXTCOLOR', (0, 0), (-2, -1), colors.black),  # Couleur de texte de l'entête
        ('FONTNAME', (0, 0), (-2, -1), 'Helvetica-Bold'),  # Style de police de la première colonne du tableau
        ('FONTSIZE', (0, 0), (-2, -1), 10),  # Taille de police de l'entête
        ('ALIGN', (0, 0), (-2, -1), 'LEFT'),  # Alignement horizontal de l'entête

        # Mise en forme du corps du tableau
        ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),  # Alignement vertical du contenu du tableau
        ('ALIGN', (0, -1), (-1, -1), 'LEFT'),  # Alignement horizontal du contenu du tableau
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),  # Couleur de texte du contenu
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica'),  # Style de police du contenu
        ('FONTSIZE', (0, -1), (-1, -1), 10),  # Taille de police du contenu

        # Bordures internes et externes
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),  # Couleur, épaisseur des bordures internes
        ('BOX', (0, 0), (-1, -1), 1, colors.black),  # Couleur, épaisseur des bordures externes

    ]))

    table_perso.drawOn(p, 150, 535)  # Je dessine le tableau dans le canvas selon les coordonnées indiquées

    # Insertion du tableau des données contenant les informations liées au salaire de l'employé
    table_salaire = Table(
        table_data_salaire)  # Permet de créer un tableau à deux (2) dimensions contenant les données stockées dans "table_data_info" declaré plus haut
    table_salaire.wrapOn(p, 400, 100)  # Je définis la largeur et la hauteur du tableau dans le canvas

    # Je procède ici à la mise en forme du tableau
    table_salaire.setStyle(TableStyle([  # Mise en forme de l'entête du tableau des données
        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),  # Alignement vertical du texte de l'entête
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),  # Couleur de texte de l'entête
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Style de police de l'entête
        ('FONTSIZE', (0, 0), (0, -1), 10),  # Taille de police de l'entête
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Alignement horizontal de l'entête

        # Mise en forme du corps du tableau
        ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),  # Alignement vertical du contenu du tableau
        ('ALIGN', (0, -1), (-1, -1), 'LEFT'),  # Alignement horizontal du contenu du tableau
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),  # Couleur de texte du contenu
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica'),  # Style de police du contenu
        ('FONTSIZE', (0, -1), (-1, -1), 10),  # Taille de police du contenu

        # Bordures internes et externes
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),  # Couleur, épaisseur des bordures internes
        ('BOX', (0, 0), (-1, -1), 1, colors.black),  # Couleur, épaisseur des bordures externes

    ]))

    table_salaire.drawOn(p, 150, 315)  # Je dessine le tableau dans le canvas selon les coordonnées indiquées

    p.setFont('Helvetica-Bold', 12)
    p.drawString(150, 505,
                 'DETAILS DU SALAIRE')  # Titre du deuxième tableau de données contenant les infos sur le salaire de l'employé

    p.setFont('Helvetica', 11)
    # Ecriture des informations du bas de la page, Date d'impression, signature du DG et de la partie reservée au parent d'élève
    p.drawString(290, 270, 'Conakry, le ')
    p.drawString(350, 270, datetime.now().strftime('%d/%m/%Y'))
    p.drawString(120, 200, 'Le Salarié')
    p.drawString(375, 200, 'La Comptabilité')
    p.drawString(375, 118, str(data_ecole[8]))

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename='Bulletin_Salaire ' + str(id_emp) + '.pdf',
                        content_type='application/pdf')


def imprimerecuavancesalaire(request, idavce):
    return HttpResponseRedirect(reverse('recuavancesalaire',
                                        args=(
                                            idavce,)))


def imprimebulletinsalaire(request, idsal):
    return HttpResponseRedirect(reverse('recubulletinsalaire',
                                        args=(
                                            idsal,)))
