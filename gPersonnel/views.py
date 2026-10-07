from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
import io
from django.http import FileResponse, HttpResponseRedirect, HttpResponse, JsonResponse
from reportlab.pdfgen import canvas

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.lib import colors  # Contient les méthodes/fonctions de gestion des couleurs
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, NextPageTemplate,
    Table, TableStyle, Paragraph, Spacer, Image, HRFlowable)
#from reportlab.platypus import Table as RLTable  # évite le conflit de nom avec votre "Table" du tableau principal
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib.utils import ImageReader, simpleSplit
from django.utils.dateparse import parse_date
import os

from PIL import Image

from django.urls import reverse
from datetime import datetime, date  # Utilisé pour recuperer l'année courante dans la generation des matricules des élèves

from django.db.models import Sum, Q
from .models import *
from .forms import *
from gComptabilite.models import *
from gComptabilite.views import affichersoldecaisse
from gAdministration.models import Ecole, Historique
from gUsers.decorators import action_requise
from core.context_processor import annee_scolaire_actuelle

# Importation des styles de tableaux définis dans le module views de l'app gEleve
from gEleve.views import style_cellule, style_totaux

# Create your views here.
# Gestion du personnel
@action_requise('personnel_gerer')
def ajouterpersonnel(request):
    if request.method == 'POST':
        formpersonnel = FormPersonnel(request.POST)
        if formpersonnel.is_valid():
            p = Personnel()
            p.nom_personnel = request.POST['nom_personnel']
            p.prenom_personnel = request.POST['prenom_personnel']
            p.civilite = request.POST['civilite']
            p.date_naissance = request.POST['date_naissance']
            p.lieu_naissance = request.POST['lieu_naissance']
            p.niveau_etude = request.POST['niveau_etude']
            p.type_personnel = request.POST['type_personnel']
            p.adresse_personnel = request.POST['adresse_personnel']
            p.contact_personnel = request.POST['contact_personnel']
            p.fonction_personnel = request.POST['fonction_personnel']
            p.email_personnel = request.POST['email_personnel']
            p.sexe_personnel = request.POST['sexe_personnel']
            p.salbase = Decimal(request.POST['salbase'])
            p.annee_experience = request.POST['annee_experience']
            p.contrat_type = request.POST['contrat_type']
            p.diplome = request.POST['diplome']
            p.date_embauche = request.POST['date_embauche']
            p.etat_matrimonial = request.POST['etat_matrimonial']

            if request.FILES.get('photo_employe'):
                p.photo_employe = request.FILES.get('photo_employe')

            an = request.POST['annee_scolaire']
            ans = AnneeScolaire.objects.get(id=an)
            p.annee_scolaire = ans
            p.save()
            
            formpersonnel = FormPersonnel()
            messages.success(request, 'Employé enregistré avec succès')
        else:
            messages.error(request,'Les données soumises sont invalides ou ne respectent pas les critères de validation du formulaire.')
    else:
        formpersonnel = FormPersonnel()

    context = {'form': formpersonnel}
    return render(request, 'gPersonnel/enregistrer_personnel.html', context)

@action_requise('personnel_gerer')
def listepersonnel(request):

    eff_total = 0
    eff_homme = 0
    eff_femme = 0

    pers = Personnel.objects.select_related('annee_scolaire').all().order_by('nom_personnel')
    ane = AnneeScolaire.objects.all().order_by('id')

    eff_total = pers.count() # C'est l'effectif total du personnel de l'école toute année confondue
    eff_homme = pers.filter(sexe_personnel__exact=SEXE_PERSONNEL[0][0]).count() # Nombre d'hommes engagés dans l'établissement
    eff_femme = pers.filter(sexe_personnel__exact=SEXE_PERSONNEL[1][0]).count() # Nombre de femmes engagées dans l'établissement


    paginepers = Paginator(pers, 20)
    numpagepers = request.GET.get('page')
    pers = paginepers.get_page(numpagepers)

    return render(request, 'gPersonnel/liste_generale_personnel.html', dict(employe=pers, ansc=ane, categorie_emp=TYPE_PERSONNEL, effectif_total=eff_total, effectif_total_homme=eff_homme, effectif_total_femme=eff_femme))


@action_requise('personnel_gerer')
def listepersonnelcategorie(request):

    eff_total = 0
    eff_homme = 0
    eff_femme = 0
     
    an = request.GET.get('annee_scolaire')
    categ = request.GET.get('categorie_employe')

    ans = AnneeScolaire.objects.get(id=an) # Permet de recuperer l'ID de l'année scolaire sélectionnée

    liste_emp_annee = {}
    liste_emp_categorie = {}

    liste_emp_annee = Personnel.objects.none()
    liste_emp_categorie = Personnel.objects.none()

    # Construction de la query string SANS le paramètre 'page'
    querydict = request.GET.copy()
    querydict.pop('page', None)
    query_string = querydict.urlencode()

    if an not in (None,''):

        liste_emp_annee = Personnel.objects.select_related('annee_scolaire').filter(annee_scolaire__exact=ans)

        eff_total = liste_emp_annee.count()
        eff_homme = liste_emp_annee.filter(sexe_personnel__exact=SEXE_PERSONNEL[0][0]).count()
        eff_femme = liste_emp_annee.filter(sexe_personnel__exact=SEXE_PERSONNEL[1][0]).count()

        paginepers = Paginator(liste_emp_annee, 20)
        numpagepers = request.GET.get('page')
        liste_emp_annee = paginepers.get_page(numpagepers)

    elif an not in (None, '') and categ not in (None, ''):

        
        liste_emp_categorie = Personnel.objects.select_related('annee_scolaire').filter(Q(annee_scolaire__exact=ans),Q(type_personnel__exact=categ))

        
        eff_total = liste_emp_categorie.count()
        eff_homme = liste_emp_categorie.filter(sexe_personnel__exact=SEXE_PERSONNEL[0][0]).count()
        eff_femme = liste_emp_categorie.filter(sexe_personnel__exact=SEXE_PERSONNEL[1][0]).count()

        paginepers = Paginator(liste_emp_categorie, 20)
        numpagepers = request.GET.get('page')
        liste_emp_categorie = paginepers.get_page(numpagepers)

    anesc = AnneeScolaire.objects.all().order_by('id') # Permet de recharger la liste des années dans le dropdown du filtre

    return render(request, 'gPersonnel/liste_generale_personnel.html', dict(ansc=anesc, categorie_emp=TYPE_PERSONNEL, employecategorie=liste_emp_categorie, employeannee=liste_emp_annee, effectif_total=eff_total, effectif_total_homme=eff_homme, effectif_total_femme=eff_femme, query_string=query_string))

@action_requise('personnel_gerer')
def editerpersonnel(request, idpers):
    pers = Personnel.objects.get(id=idpers)
    ans = AnneeScolaire.objects.all().order_by('id')

    context = {'pers': pers, 'civilite': CIVILITE_CHOICES, 'categorie': TYPE_PERSONNEL, 'sexep':SEXE_PERSONNEL, 'typecontrat': CONTRAT_CHOICES, 'statut': STATUT_MATRIMONIAL, 'ansc':ans}

    return render(request, 'gPersonnel/modifier_personnel.html', context)


@action_requise('personnel_gerer')
def detailspersonnel(request, idpers):
    pers = Personnel.objects.get(id=idpers)
    return render(request, 'gPersonnel/afficher_details_personnel.html', dict(pers=pers))


@action_requise('personnel_gerer')
def modifierpersonnel(request, idpers):

    if request.method == 'POST':
        pers = Personnel.objects.get(id=idpers)
        pers.nom_personnel = request.POST['nom_personnel']
        pers.prenom_personnel = request.POST['prenom_personnel']
        pers.civilite = request.POST['civilite']
        pers.date_naissance = request.POST['date_naissance']
        pers.lieu_naissance = request.POST['lieu_naissance']
        pers.niveau_etude = request.POST['niveau_etude']
        pers.type_personnel = request.POST['type_personnel']
        pers.adresse_personnel = request.POST['adresse_personnel']
        pers.contact_personnel = request.POST['contact_personnel']
        pers.fonction_personnel = request.POST['fonction_personnel']
        pers.email_personnel = request.POST['email_personnel']
        pers.sexe_personnel = request.POST['sexe_personnel']
        pers.salbase = Decimal(request.POST['salaire_base'])
        pers.annee_experience = request.POST['annee_experience']
        pers.contrat_type = request.POST['type_contrat']
        pers.diplome = request.POST['diplome_personnel']
        pers.date_embauche = request.POST['date_embauche']
        pers.etat_matrimonial = request.POST['etat_matrimonial']

        if request.FILES.get('photo_employe'):
            pers.photo_employe = request.FILES.get('photo_employe')

        an = request.POST.get('annee_scolaire')
        ans = AnneeScolaire.objects.get(id=an)
        pers.annee_scolaire = ans
        pers.save()

        return redirect('../listegeneralepersonnel/')
    else:
        return redirect('../listegeneralepersonnel/')

@action_requise('personnel_gerer')
def supprimerpersonnel(request, pk):
    pers = Personnel.objects.get(id=pk)
    pers.delete()
    return redirect('../listegeneralepersonnel/')


"""
Rapport « Liste du personnel » (générale ou par catégorie) — ReportLab, A4 paysage.

À COLLER dans le même module que `generer_rapport_matriculation`, dont il réutilise
les imports et les styles (style_entete_col, style_cellule, style_totaux).

Les colonnes reprennent exactement celles de ton tableau HTML (listegeneralepersonnel),
en enlevant Photo et Actions — comme ton propre export Excel/PDF datatable le fait déjà
avec exportOptions: { columns: ':not(.no-export)' }.
"""


def generer_rapport_personnel(request, data_ecole, annee, titre_rapport, categorie=None):
    """
    categorie=None  -> liste générale (tous les employés de l'année scolaire)
    categorie='...' -> uniquement les employés dont type_personnel == categorie
    """
    marge_gauche_droite = 1.5*cm
    marge_bas = 1.5*cm
    largeur_frame = landscape(A4)[0] - 2*marge_gauche_droite

    an = AnneeScolaire.objects.get(id=annee)

    # --- 1. Récupération des données ---
    requete = Personnel.objects.select_related('annee_scolaire').filter(annee_scolaire__exact=an)
    if categorie is not None:
        requete = requete.filter(type_personnel__exact=categorie)
    requete = requete.order_by('type_personnel', 'nom_personnel', 'prenom_personnel')

    listgenerale = list(requete)  # une seule requête SQL, réutilisée pour le tableau ET les totaux
    effectif_total = len(listgenerale)

    if effectif_total == 0:
        messages.error(request, "Aucun employé trouvé pour les critères donnés.")
        return None

    # --- 2. Construction du tableau (mêmes colonnes que la liste générale du personnel) ---

    style_entete_perso = ParagraphStyle(
        'EnteteListePersonnel', parent=getSampleStyleSheet()['Normal'],
        fontName='Helvetica-Bold', fontSize=6.5, leading=7.5, textColor=colors.white,
    )

    entetes = ['ID', 'Nom & Prénom(s)', 'Date naiss', 'Lieu naiss',
               'Catégorie', 'Résidence', 'Contact', 'Poste occupé',
               'Email', 'Genre', 'Salbase','Contrat','Diplôme', 'Date emb', 'Statut Mat', 'Année scolaire']
    table_data = [[Paragraph(e, style_entete_perso) for e in entetes]]

    # Compteurs pour la ligne de totaux, remplis au fil de la même boucle que le tableau
    total_par_sexe = {}       # ex. {'H': 24, 'F': 12}
    total_par_categorie = {}  # ex. {'Vacataire': 24, 'Permanent': 12} — utile seulement en liste générale

    for emp in listgenerale:

        total_par_sexe[emp.sexe_personnel] = total_par_sexe.get(emp.sexe_personnel, 0) + 1
        total_par_categorie[emp.type_personnel] = total_par_categorie.get(emp.type_personnel, 0) + 1

        ligne_brute = [
            emp.id,
            f"{emp.nom_personnel} {emp.prenom_personnel}",
            emp.date_naissance.strftime('%d/%m/%Y') if emp.date_naissance else '',
            emp.lieu_naissance,
            emp.type_personnel,
            emp.adresse_personnel,
            emp.contact_personnel,
            emp.fonction_personnel,
            emp.email_personnel,
            emp.sexe_personnel,
            f"{emp.salbase:.2f}" if emp.salbase is not None else '',
            emp.contrat_type,
            emp.diplome,
            emp.date_embauche.strftime('%d/%m/%Y') if emp.date_embauche else '',
            emp.etat_matrimonial,
            str(emp.annee_scolaire),
        ]
        ligne = [Paragraph(str(v) if v else '', style_cellule) for v in ligne_brute]
        table_data.append(ligne)

    # --- Ligne des totaux : "Effectif de l'école" (colonnes 0-9) + détail (colonnes 10-19) ---
    texte_totaux = f"Total : {effectif_total}"
    for libelle, n in total_par_sexe.items():
        texte_totaux += f"    —    {libelle} : {n}"

    if categorie is None:
        detail_categ = "    —    ".join(f"{libelle} : {n}" for libelle, n in total_par_categorie.items())
        texte_totaux += f"<br/>{detail_categ}"
    else:
        texte_totaux += f"<br/>Catégorie : {list(total_par_categorie.keys())[0]}"

    table_data.append([
        Paragraph('Effectif du personnel', style_totaux), '', '', '', '', '', '', '',
        Paragraph(texte_totaux, style_totaux), '', '', '', '', '', '', '',
    ])

    # Largeurs proportionnelles : ID très étroit, Nom & Prénom(s) large, et chaque colonne
    # au moins assez large pour que son en-tête tienne sur une seule ligne (calculé pour
    # style_entete_perso, taille 6.5 pt). Largeur d'"Exp." reversée sur Salaire.
    poids = [20.5, 89.8, 45.5, 45.8, 44.0, 52.5, 43.2, 63.2, 35.3, 40.3, 62.0, 45.1, 42.1, 44.5, 50.7, 50.5]
    somme_poids = sum(poids)
    col_widths = [(p / somme_poids) * largeur_frame for p in poids]

    table = Table(table_data, repeatRows=1, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2980b9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f5f5f5')]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#27ae60')),
        ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
        ('SPAN', (0, -1), (7, -1)),
        ('SPAN', (8, -1), (15, -1)),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))

    # --- 3. Éléments du flux ---
    elements = [NextPageTemplate('Suivantes'), Spacer(1, 0.3*cm)]
    elements.append(table)
    elements.append(Spacer(1, 0.3*cm))

    style_signature = ParagraphStyle('Signature', parent=getSampleStyleSheet()['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold')
    date_str = datetime.now().strftime('%d/%m/%Y')

    bloc_signature = [
        [Paragraph(f"Conakry, le {date_str}", style_signature)],
        [Spacer(1, 0.1*cm)],
        [Paragraph("Le Service Scolarité", style_signature)],
        [Spacer(1, 0.6*cm)],
        [Paragraph(str(data_ecole[8]) if len(data_ecole) > 8 and data_ecole[8] else '', style_signature)],
    ]
    table_signature = Table(bloc_signature, colWidths=[largeur_frame])
    table_signature.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(table_signature)

    # --- 4. En-tête (page 1 uniquement) — identique au registre de matriculation ---
    def draw_entete(canvas_obj, doc):
        width, height = landscape(A4)
        marge = marge_gauche_droite
        largeur_utile = largeur_frame

        nom_ecole = data_ecole[0] if len(data_ecole) > 0 else ''
        ville = data_ecole[1] if len(data_ecole) > 1 else ''
        commune = data_ecole[2] if len(data_ecole) > 2 else ''
        tel1 = data_ecole[3] if len(data_ecole) > 3 else ''
        tel2 = data_ecole[4] if len(data_ecole) > 4 else ''
        logo_chemin = data_ecole[5] if len(data_ecole) > 5 else ''
        devise = data_ecole[6] if len(data_ecole) > 6 else ''
        dsee = data_ecole[7] if len(data_ecole) > 7 else ''

        y = height - 20

        canvas_obj.setFillColor(colors.black)
        canvas_obj.setFont('Helvetica-Bold', 9)
        canvas_obj.drawString(marge, y, 'MEPU-A')
        y -= 12
        canvas_obj.drawString(marge, y, 'IRE : ')
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.drawString(marge + 30, y, str(ville))
        y -= 12
        canvas_obj.setFont('Helvetica-Bold', 9)
        canvas_obj.drawString(marge, y, 'DCE : ')
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.drawString(marge + 30, y, str(commune))
        y -= 12
        canvas_obj.setFont('Helvetica-Bold', 9)
        canvas_obj.drawString(marge, y, 'DSEE : ')
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.drawString(marge + 30, y, str(dsee))
        y -= 12
        canvas_obj.setFont('Helvetica-Bold', 9)
        canvas_obj.drawString(marge, y, 'TEL : ')
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.drawString(marge + 30, y, f"{tel1} / {tel2}")

        if logo_chemin and logo_chemin != 'Logo':
            try:
                img = Image.open(logo_chemin)
                img = img.resize((60, 40), Image.LANCZOS)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                logo_buffer = io.BytesIO()
                img.save(logo_buffer, format='PNG')
                logo_buffer.seek(0)
                canvas_obj.drawImage(ImageReader(logo_buffer), width/2 - 30, height - 55, 60, 40)
            except Exception:
                pass

        y_drapeau = height - 20
        canvas_obj.setFillColor('Red')
        canvas_obj.rect(width - marge - 90, y_drapeau, 30, 8, stroke=False, fill=True)
        canvas_obj.setFillColor('yellow')
        canvas_obj.rect(width - marge - 60, y_drapeau, 30, 8, stroke=False, fill=True)
        canvas_obj.setFillColor('green')
        canvas_obj.rect(width - marge - 30, y_drapeau, 30, 8, stroke=False, fill=True)
        canvas_obj.setFillColor(colors.black)

        canvas_obj.setFont('Helvetica-Bold', 9)
        canvas_obj.drawRightString(width - marge, y_drapeau - 12, 'République de Guinée')
        canvas_obj.setFont('Helvetica-Oblique', 8)
        canvas_obj.drawRightString(width - marge, y_drapeau - 24, 'Travail-Justice-Solidarité')

        y = height - 70
        canvas_obj.setFont('Helvetica-Bold', 12)
        nom_x = (width - canvas_obj.stringWidth(str(nom_ecole), 'Helvetica-Bold', 12)) / 2
        canvas_obj.drawString(nom_x, y, str(nom_ecole))

        if devise:
            y -= 13
            canvas_obj.setFont('Helvetica-Oblique', 8)
            devise_x = (width - canvas_obj.stringWidth(str(devise), 'Helvetica-Oblique', 8)) / 2
            canvas_obj.drawString(devise_x, y, str(devise))

        y -= 10
        canvas_obj.line(marge, y, marge + largeur_utile, y)

        y -= 15
        titre = titre_rapport.upper()
        canvas_obj.setFont('Helvetica-Bold', 11)
        titre_x = (width - canvas_obj.stringWidth(titre, 'Helvetica-Bold', 11)) / 2
        canvas_obj.drawString(titre_x, y, titre)

        y -= 6
        canvas_obj.line(marge + 60, y, marge + largeur_utile - 60, y)

        y -= 16
        annee_str = an.descript_annee if an else ''
        session = annee_str.split('-')[-1] if '-' in annee_str else annee_str
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.drawString(marge + 160, y, 'Année Scolaire : ')
        canvas_obj.setFont('Helvetica', 10)
        canvas_obj.drawString(marge + 270, y, annee_str)
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.drawString(marge + 370, y, 'Session : ')
        canvas_obj.setFont('Helvetica', 10)
        canvas_obj.drawString(marge + 420, y, session)

        return y

    def draw_page_number(canvas_obj, doc):
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.drawRightString(landscape(A4)[0] - 1.5*cm, 1.0*cm, f"Page {doc.page}")
        canvas_obj.restoreState()

    def on_first_page(canvas_obj, doc):
        draw_entete(canvas_obj, doc)
        draw_page_number(canvas_obj, doc)

    def on_later_pages(canvas_obj, doc):
        draw_page_number(canvas_obj, doc)

    # --- 5. Construction avec deux PageTemplate ---
    buffer = io.BytesIO()

    y_fin_entete = 450
    hauteur_frame_page1 = y_fin_entete - marge_bas

    frame_page1 = Frame(marge_gauche_droite, marge_bas, largeur_frame, hauteur_frame_page1, id='page1', showBoundary=0, topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)

    frame_suivantes = Frame(marge_gauche_droite, marge_bas, largeur_frame, landscape(A4)[1] - marge_bas - 1.5*cm, id='suivantes', showBoundary=0, topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)

    doc = BaseDocTemplate(buffer, pagesize=landscape(A4), title=titre_rapport)
    doc.addPageTemplates([
        PageTemplate(id='Premiere', frames=frame_page1, onPage=on_first_page),
        PageTemplate(id='Suivantes', frames=frame_suivantes, onPage=on_later_pages),
    ])

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ----------------------------------------------------------------------
# Vues Django — même principe que ta vue existante pour le registre de matriculation
# ----------------------------------------------------------------------
def _generer_rapport_personnel(request, nom_fichier, titre, categorie=None):
    annee = request.GET.get('annee')
    if not annee:
        messages.error(request, "Veuillez sélectionner une année scolaire.")
        return redirect('listegeneralepersonnel')

    # Tuple data_ecole (indices 0 à 8) attendu par l'en-tête — même contrat que
    # pour le registre de matriculation. Si ton wrapper le construit déjà,
    # reprends cette partie telle quelle.
    ecole = Ecole.objects.first()
    data_ecole = (
        ecole.nom_ecole, ecole.ville_ecole, ecole.prefect_commune,
        ecole.telephone1, ecole.telephone2 if ecole.telephone2 else '',
        ecole.logo_ecole.path if ecole.logo_ecole else '',
        ecole.devise_ecole, ecole.dsee, ecole.dg,
    )

    buffer = generer_rapport_personnel(request, data_ecole, annee, titre, categorie)
    if buffer is None:
        return redirect('listegeneralepersonnel')

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nom_fichier}.pdf"'
    return response


@action_requise('personnel_gerer')
def rapportgeneralpersonnel(request):
    """Liste générale du personnel (tous les employés de l'année scolaire choisie)."""
    return _generer_rapport_personnel(
        request, nom_fichier='Liste_generale_personnel', titre="REGISTRE ANNUEL DU PERSONNEL")


@action_requise('personnel_gerer')
def rapportpersonnelcategorie(request):
    """Liste du personnel filtrée sur une catégorie (type_personnel)."""
    categorie = request.GET.get('categorie')
    if not categorie:
        messages.error(request, "Veuillez sélectionner une catégorie.")
        return redirect('listegeneralepersonnel')
    return _generer_rapport_personnel(
        request, nom_fichier='Liste_personnel_par_categorie',
        titre="REGISTRE DU PERSONNEL PAR CATEGORIE", categorie=categorie)


# Cette fonction est utilisée au niveau du template de gestion des avances sur salaire
@action_requise('personnel_gerer')
def chargerinfoemploye(request):
    idemploye = request.GET.get('idemploye')
    try:
        p = Personnel.objects.get(id=idemploye)
        data = {
            'nom': p.nom_personnel,
            'prenom': p.prenom_personnel,
            'contact': p.contact_personnel,
            'type_employe': p.type_personnel,
            'photo_employe': str(p.photo_employe) if p.photo_employe else '',
        }
    except Personnel.DoesNotExist:
        data = {'nom': '', 'prenom': '', 'contact': '', 'type_employe': '', 'photo_employe': ''}
    
    return JsonResponse(data)


# Cette autre est utilisée au niveau du template de gestion des salaires
@action_requise('personnel_salaire')
def charger_infospersonnel(request):

    idemp = request.GET.get('idemploye')
    mois = request.GET.get('mois')
    idannee = request.GET.get('idannee')

    try:
        emp = Personnel.objects.get(pk=idemp)
    except (Personnel.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'erreur': 'Employé introuvable'}, status=404)

    total = AvanceSalaire.objects.filter(
        idpersonnel=emp,
        mois_avance=mois,
        anscolaire_id=idannee,
    ).aggregate(s=Sum('montant_avance'))['s']
    avances = total if total is not None else 0

    # salbase n'est pas nullable (default=0), donc pas de test None nécessaire
    base = emp.salbase if emp.type_personnel == TYPE_PERSONNEL[1][0] else 0

    return JsonResponse({
        'nom': emp.nom_personnel,
        'prenom': emp.prenom_personnel,
        'contact': emp.contact_personnel,
        'type_employe': emp.type_personnel,
        'salbase': float(base),
        'avances': float(avances),
    })

# Fonction permettant de convertir les valeurs numériques recupérées depuis le formulaire gestion des salaires et mis à jour des salaires en Decimal
def to_decimal(valeur):
    """Convertit '3,500,000.00', '1 000,50' ou '1.234.567,89' en Decimal."""
    if valeur is None:
        return Decimal('0')
    s = str(valeur).replace('\xa0', '').replace('\u202f', '').replace(' ', '').strip()
    if s == '':
        return Decimal('0')

    last_dot, last_comma = s.rfind('.'), s.rfind(',')
    if last_dot != -1 and last_comma != -1:
        s = s.replace(',', '') if last_dot > last_comma else s.replace('.', '').replace(',', '.')
    elif last_comma != -1:
        parts = s.split(',')
        if len(parts) == 2 and len(parts[1]) <= 2:
            s = parts[0] + '.' + parts[1]
        else:
            s = s.replace(',', '')
    elif s.count('.') > 1:
        s = s.replace('.', '')

    try:
        return Decimal(s)
    except InvalidOperation:
        raise ValueError("Valeur numérique invalide : {}".format(valeur))

# Gestion des Salaires
@action_requise('personnel_salaire')
def enregistrersalaire(request):

    mois_paye = None
    if request.method == 'POST':
        formsalaire = FormSalaire(request.POST)
        if formsalaire.is_valid():
            ansc = request.POST.get('anneescolaire')
            ans = AnneeScolaire.objects.get(id=ansc)
            idper = request.POST.get('idpersonnel')
            idp = Personnel.objects.get(id=idper)
            date_paiement = parse_date(request.POST.get('date_paiement', ''))              

            typers = idp.type_personnel

            total_avance = 0
            cotis = 0

            mois_paye = request.POST.get('mois_paie')
            

            # Je tente de recuperer ici le montant des avances sur salaire de l'employé selectionné durant le mois sélectionné et l'année scolaire sélectionnée
            mavce = AvanceSalaire.objects.filter(Q(idpersonnel__exact=idp),Q(anscolaire__exact=ans),Q(mois_avance__exact=mois_paye)).aggregate(tavance=Sum('montant_avance'))
            
            if mavce['tavance'] is not None:
                total_avance = mavce['tavance']
            else:
                total_avance = 0

            
            if date_paiement is None:
                messages.error(request, "La date de paiement est invalide.")
            else:
                sal = Salaire()
                sal.mois_paie = mois_paye
                sal.date_paiement = date_paiement
                sal.detail_paiement = request.POST['detail_paiement']
                nbheure = int(to_decimal(request.POST['nbre_heure']))
                thoraire = to_decimal(request.POST['taux_horaire'])
                sal.anneescolaire = ans
                sal.idpersonnel = idp
                sal.avance_paie = Decimal(total_avance)
                sal.primes = to_decimal(request.POST['primes'])
                sal.nb_hsupp = int(to_decimal(request.POST['nb_hsupp']))
                sal.mont_hsupp = to_decimal(request.POST['mont_hsupp'])
                cotis = to_decimal(request.POST.get('cotis_sociale'))

                salb = 0
                if typers == TYPE_PERSONNEL[1][0]:  # TYPE_PERSONNEL[1][0] == 'Permanent'
                    salb = Decimal(idp.salbase)
                elif typers == TYPE_PERSONNEL[0][0]:  # TYPE_PERSONNEL[0][0] == 'Vacataire'
                    sal.nbre_heure = int(nbheure)
                    sal.taux_horaire = Decimal(thoraire)
                    salb = Decimal(thoraire) * Decimal(nbheure)

                sb = (salb + Decimal(sal.primes) + Decimal(sal.mont_hsupp)) - Decimal(total_avance)
                sal.salbrut = sb
                sal.cotis_sociale = cotis
                snet = sb  - cotis
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
                    cais.date_operation = date_paiement
                    cais.save()
                    messages.success(request, 'Salaire enregistré avec succès')

                    # Ici je vais enregistrer l'evenement dans la table Historique
                    his = Historique()
                    his.nature_operation = CATEGORIE_DEPENSE_CHOICES[1][1]
                    his.detail_operation = 'Paiement du salaire de l\'employé : {}, {}, {}, pour le mois de {}'.format(
                        sal.idpersonnel.id, idp.nom_personnel, idp.prenom_personnel, sal.mois_paie)
                    his.user_login = 'contact@universtechgroup.com'
                    his.save()

                    

                    # Ici je vais recuperer le dernier ID salaire en vue de pouvoir imprimer le bulletin de salaire
                    idsal = Salaire.objects.latest('id')
                    lastid = idsal.id  # Permet de recuperer l'ID de ce dernier record

                    return redirect('confirmerimpression', lastid)

                else:
                    messages.error(request, 'Impossible de valider cette opération car le solde caisse est insuffisant')
    else:
        formsalaire = FormSalaire()

    context = {'form': formsalaire,}
    
    return render(request, 'gPersonnel/enregistrer_salaire.html', context)


@action_requise('personnel_salaire')
def listemensuellesalaire(request):

    datejour = date.today()
    mois_courant = str(datejour.month) # Permet de recuperer le numéro du mois, utile pour le queryset ci dessous
    nom_mois = datejour.strftime('%B') # Permet de recuperer le nom intégral du mois, utile pour l'affichage dans le template
    
    annee_encours = annee_scolaire_actuelle(request)['annee_scolaire'] # annee_scolaire_actuelle vient du core/context_processor/
    
    an = AnneeScolaire.objects.get(descript_annee=annee_encours) # Je tente de recuperer l'ID de l'année scolaire courante fournie à partir du context_processor
    anescoid = an.id

    liste_mensuelle = Salaire.objects.select_related('anneescolaire', 'idpersonnel').filter(Q(anneescolaire__exact=anescoid),Q(mois_paie__exact=mois_courant)).order_by('idpersonnel')
    
    mont_base = liste_mensuelle.aggregate(tbase=Sum('idpersonnel__salbase'))

    mont_primes = liste_mensuelle.aggregate(tprimes=Sum('primes'))
    mont_brut = liste_mensuelle.aggregate(tbrut=Sum('salbrut'))
    mont_avance = liste_mensuelle.aggregate(tavances=Sum('avance_paie'))
    mont_net = liste_mensuelle.aggregate(tnet=Sum('salnet'))

    total_salbase = 0
    total_primes = 0
    total_salbrut = 0
    total_avance = 0
    total_salnet = 0

    if mont_base['tbase'] is not None:
        total_salbase = mont_base['tbase']
    else:
        total_salbase = 0

    if mont_primes['tprimes'] is not None:
        total_primes = mont_primes['tprimes']
    else:
        total_primes = 0

    if mont_brut['tbrut'] is not None:
        total_salbrut = mont_brut['tbrut']
    else:
        total_salbrut = 0

    if mont_avance['tavances'] is not None:
        total_avance = mont_avance['tavances']
    else:
        total_avance = 0

    if mont_net['tnet'] is not None:
        total_salnet = mont_net['tnet']
    else:
        total_salnet = 0

    soldec = affichersoldecaisse()  # Je recupère le dernier solde caisse après l'opération

    an = AnneeScolaire.objects.all().order_by('id')

    paginesalaire = Paginator(liste_mensuelle, 20)
    numpagesalaire = request.GET.get('page')
    liste_mensuelle = paginesalaire.get_page(numpagesalaire)

    context = {'salaire_mensuel': liste_mensuelle, 'total_salbase': total_salbase, 'total_primes': total_primes, 'total_salbrut': total_salbrut, 'total_avance': total_avance, 'total_salnet': total_salnet, 'solde_caisse': soldec, 'mois_actuel': nom_mois, 'annee': an}

    return render(request, 'gPersonnel/liste_salaire.html', context)


@action_requise('personnel_salaire')
def listeperiodiquesalaire(request):

    ane = request.GET.get('nom_annee')
    debut = request.GET.get('ddebut')
    fin = request.GET.get('dfin')

    listeperiode = {}
    listeperiode = Salaire.objects.none()
        
    querydict = request.GET.copy()
    querydict.pop('page', None)
    query_string = querydict.urlencode()
    
    if ane not in (None, '') and debut not in (None, '') and fin not in (None, ''):
    
        debut = datetime.strptime(debut,'%Y-%m-%d')
        fin = datetime.strptime(fin,'%Y-%m-%d')

        listeperiode = Salaire.objects.select_related('anneescolaire', 'idpersonnel').filter(Q(anneescolaire__exact=ane),Q(date_paiement__range=(debut,fin))).order_by('idpersonnel')
        
        mont_base = listeperiode.aggregate(tbase=Sum('idpersonnel__salbase'))
        
        mont_primes = listeperiode.aggregate(tprimes=Sum('primes'))
        mont_brut = listeperiode.aggregate(tbrut=Sum('salbrut'))
        mont_avance = listeperiode.aggregate(tavances=Sum('avance_paie'))
        mont_net = listeperiode.aggregate(tnet=Sum('salnet'))
        
        total_salbase = 0
        total_primes = 0
        total_salbrut = 0
        total_avance = 0
        total_salnet = 0
        
        if mont_base['tbase'] is not None:
            total_salbase = mont_base['tbase']
        else:
            total_salbase = 0
        
        if mont_primes['tprimes'] is not None:
            total_primes = mont_primes['tprimes']
        else:
            total_primes = 0
        
        if mont_brut['tbrut'] is not None:
            total_salbrut = mont_brut['tbrut']
        else:
            total_salbrut = 0
        
        if mont_avance['tavances'] is not None:
            total_avance = mont_avance['tavances']
        else:
            total_avance = 0
        
        if mont_net['tnet'] is not None:
            total_salnet = mont_net['tnet']
        else:
            total_salnet = 0
    
    soldec = affichersoldecaisse()  # Je recupère le dernier solde caisse après l'opération
    
    an = AnneeScolaire.objects.all().order_by('id')
    
    paginesalaire = Paginator(listeperiode, 20)
    numpagesalaire = request.GET.get('page')
    listeperiode = paginesalaire.get_page(numpagesalaire)
    
    context = {'salaire_periode': listeperiode, 'total_salbase': total_salbase, 'total_primes': total_primes, 'total_salbrut': total_salbrut, 'total_avance': total_avance, 'total_salnet': total_salnet, 'solde_caisse': soldec, 'annee': an, 'query_string': query_string, 'ddebut': debut, 'dfin': fin,}

    return render(request, 'gPersonnel/liste_salaire.html', context)

    

@action_requise('personnel_salaire')
def confirmerimpression(request, id):
    sal = get_object_or_404(Salaire, pk=id)
    return render(request, 'gPersonnel/confirmer_impression.html', {'sal': sal})


@action_requise('personnel_salaire')
def editersalaire(request, idsal):
    sal = Salaire.objects.get(id=idsal)
    ane = AnneeScolaire.objects.all().order_by('id')
    emp = Personnel.objects.all().order_by('id')

    context = {'sal': sal, 'ansc': ane, 'liste_emp': emp, 'mois_paye': MOIS_CHOICES,}

    return render(request, 'gPersonnel/modifier_salaire.html', context)


@action_requise('personnel_salaire')
def detailssalaire(request, idsal):
    sal = Salaire.objects.get(id=idsal)
    return render(request, 'gPersonnel/afficher_details_salaire.html', dict(sal=sal))


@action_requise('personnel_salaire')
def modifiersalaire(request, idsal):

    sal = get_object_or_404(Salaire, pk=idsal)

    if request.method == 'POST':
        emp = get_object_or_404(Personnel, pk=request.POST.get('idpersonnel'))
        annee = get_object_or_404(AnneeScolaire, pk=request.POST.get('anneescolaire'))
        mois = request.POST.get('mois_paie')
        date_paiement = parse_date(request.POST.get('date_paiement', ''))

        # if date_paiement is None:
        #     messages.error(request, "La date de paiement est invalide.")
        #     return redirect('modifiersalaire', sal.id)

        try:
            primes = to_decimal(request.POST.get('primes'))
            cotis = to_decimal(request.POST.get('cotis_sociale'))
            mont_hsupp = to_decimal(request.POST.get('mont_hsupp'))
            nb_hsupp = int(to_decimal(request.POST.get('nb_hsupp')))
            nbre_heure = int(to_decimal(request.POST.get('nbre_heure')))
            taux_horaire = to_decimal(request.POST.get('taux_horaire'))
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('modifiersalaire', sal.id)

        # Avances du mois et de l'année sélectionnés (recalculées, jamais reprises du formulaire)
        total_avances = AvanceSalaire.objects.filter(
            idpersonnel=emp,
            mois_avance=mois,
            anscolaire=annee,
        ).aggregate(s=Sum('montant_avance'))['s']
        avances = total_avances if total_avances is not None else Decimal('0')

        # Salaire de base selon la catégorie
        if emp.type_personnel == TYPE_PERSONNEL[0][0]: # Quand c'est Vacataire
            salbase = Decimal(nbre_heure) * taux_horaire
        elif emp.type_personnel == TYPE_PERSONNEL[1][0]:  # Permanent
            salbase = emp.salbase
            nbre_heure = 0
            taux_horaire = Decimal('0')

        salbrut = salbase + primes + mont_hsupp - avances
        salnet = salbrut - cotis

        sal.idpersonnel = emp
        sal.anneescolaire = annee
        sal.mois_paie = mois
        sal.date_paiement = date_paiement
        sal.nbre_heure = nbre_heure
        sal.taux_horaire = taux_horaire
        sal.avance_paie = avances
        sal.primes = primes
        sal.salbrut = salbrut
        sal.cotis_sociale = cotis
        sal.salnet = salnet
        sal.nb_hsupp = nb_hsupp
        sal.mont_hsupp = mont_hsupp
        sal.detail_paiement = 'Paiement du salaire de {} {} , Contact : {} , Catégorie : {}'.format(
            emp.nom_personnel, emp.prenom_personnel, emp.contact_personnel, emp.type_personnel
        )
        sal.save()
          
        return redirect('../listesalairemensuel/')
    else:
        return redirect('../listesalairemensuel/')


@action_requise('personnel_salaire')
def supprimersalaire(request, pk):
    sal = Salaire.objects.get(id=pk)
    sal.delete()
    return redirect('../listesalairemensuel/')


# Gestion des Avances sur Salaire
@action_requise('personnel_avance_salaire')
def valideravancesalaire(request):

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        formavancesalaire = FormAvanceSalaire(request.POST)

        def erreur_response(message):
            """Centralise le renvoi d'erreur : JSON pour l'AJAX, message Django sinon."""
            if not is_ajax:
                messages.error(request, message)
            if is_ajax:
                return JsonResponse({'success': False, 'error': message})
            return None # signale à l'appelant de continuer vers le render classique

        if formavancesalaire.is_valid():
            idpers = request.POST.get('idpersonnel')
            ans = request.POST.get('anscolaire')
            idp = Personnel.objects.get(id=idpers)
            anc = AnneeScolaire.objects.get(id=ans)

            avc = AvanceSalaire()
            avc.mois_avance = request.POST['mois_avance']
            avc.intitule = request.POST['intitule']
            avc.date_avance = request.POST['date_avance']
            mont_avce = Decimal(request.POST['montant_avance'])
            avc.montant_avance = mont_avce

            avc.anscolaire = anc
            avc.idpersonnel = idp

            soldec = affichersoldecaisse()

            if soldec > mont_avce:
                avc.save()

                cais = Caisse()
                cais.anscolaire = anc
                cais.libelle_operation = f'Paiement avance sur salaire de l\'employé, ID : {avc.idpersonnel.id} {idp.nom_personnel} {idp.prenom_personnel}, pour le mois de {avc.get_mois_avance_display().capitalize()}'
                cais.montant_encaisse = mont_avce
                cais.solde_actuel = soldec - mont_avce
                cais.categ_depense = CATEGORIE_DEPENSE_CHOICES[1][1]
                cais.type_operation = TYPE_OPERATION_CAISSE_CHOICES[2][1]
                cais.date_operation = request.POST['date_avance']
                cais.save()

                # Ici je vais enregistrer l'evenement dans la table Historique
                his = Historique()
                his.nature_operation = 'Avance sur salaire'
                his.detail_operation = 'Paiement de l\'avance sur salaire de l\'employé : {}, {}, {}, pour le mois de {}'.format(avc.idpersonnel.id, idp.nom_personnel, idp.prenom_personnel, avc.get_mois_avance_display().capitalize())
                his.user_login = 'contact@universtechgroup.com'
                his.save()

                message_succes= 'Avance sur salaire validée avec succès.'

                if not is_ajax:
                    messages.success(request, message_succes)

                formavancesalaire = FormAvanceSalaire() # Vider les champs avant de rediriger vers l'impression

                # Ici je vais recuperer le dernier ID avance salaire en vue de pouvoir imprimer le recu d'avance sur salaire
                idavce = AvanceSalaire.objects.latest('id')

                lastid = idavce.id  # Permet de recuperer l'ID de ce dernier record

                # Ce contrôle permet d'ouvrir le reçu de paiement dans un nouvel onglet du navigateur
                if is_ajax:
                    return JsonResponse({
                    'success': True,
                    'message': message_succes,
                    'recu_url': reverse('recuavancesalaire', args=(lastid,))
                    })

                return HttpResponseRedirect(reverse('recuavancesalaire',
                                                    args=(
                                                        lastid,)))
            else:

                message = 'Impossible de valider cette opération car le solde caisse est insuffisant'
                if not is_ajax:
                    messages.error(request, message)

                if is_ajax:
                    return JsonResponse({'success': False, 'error': message})
        else:
            message = 'Les données soumises ne respectent pas les critères de validation du formulaire'
            if not is_ajax:
                messages.error(request,message)
            
            if is_ajax:
                return JsonResponse({'success': False, 'error': message})
            
        
    else:
        formavancesalaire = FormAvanceSalaire()
    
    return render(request, 'gPersonnel/enregistrer_avance_salaire.html', dict(form=formavancesalaire))


@action_requise('personnel_avance_salaire')
def listeavancesalaire(request):

    datejour = date.today()
    mois_courant = str(datejour.month) # Permet de recuperer le numéro du mois, utile pour le queryset ci dessous
    nom_mois = datejour.strftime('%B') # Permet de recuperer le nom intégral du mois, utile pour l'affichage dans le template

    annee_encours = annee_scolaire_actuelle(request)['annee_scolaire'] # annee_scolaire_actuelle vient du core/context_processor/

    an = AnneeScolaire.objects.get(descript_annee=annee_encours) # Je tente de recuperer l'ID de l'année scolaire courante fournie à partir du context_processor
    anescoid = an.id

    avsal = AvanceSalaire.objects.select_related('idpersonnel', 'anscolaire').filter(Q(mois_avance__exact=mois_courant),Q(anscolaire__exact=anescoid)).order_by('-date_avance') # Permet d'afficher la liste des avances sur salaire du mois en cours de l'année scolaire courante triée par date décroissante

    ans = AnneeScolaire.objects.all().order_by('id')

    mont_total = avsal.aggregate(montavance=Sum('montant_avance'))

    total_avance = 0
    total_avance = mont_total['montavance']

    soldec = affichersoldecaisse()  # Je recupère le dernier solde caisse

    pagineavance = Paginator(avsal, 20)
    numpageavance = request.GET.get('page')
    avsal = pagineavance.get_page(numpageavance)

    context = {'avancemois': avsal, 'total_avance': total_avance, 'solde_dispo': soldec, 'annee': ans, 'mois_actuel': nom_mois}

    return render(request,'gPersonnel/liste_avance_salaire.html', context)


@action_requise('personnel_avance_salaire')
def filtrelisteavancesalaire(request):

    ane = request.GET.get('nom_annee')
    debut = request.GET.get('ddebut')
    fin = request.GET.get('dfin')

    listeperiode = {}
    listeperiode = AvanceSalaire.objects.none()
    total_avance = 0

    querydict = request.GET.copy()
    querydict.pop('page', None)
    query_string = querydict.urlencode()

    if ane not in (None, '') and debut not in (None, '') and fin not in (None, ''):

        debut = datetime.strptime(debut,'%Y-%m-%d')
        fin = datetime.strptime(fin,'%Y-%m-%d')

        listeperiode = AvanceSalaire.objects.select_related('idpersonnel', 'anscolaire').filter(Q(anscolaire__exact=ane),Q(date_avance__range=(debut,fin)))

        mont_total = listeperiode.aggregate(montavance=Sum('montant_avance'))
        
        total_avance = 0
        total_avance = mont_total['montavance']   
   
    soldec = affichersoldecaisse()  # Je recupère le dernier solde caisse 
    annee = AnneeScolaire.objects.all().order_by('id')

    
    pagineavance = Paginator(listeperiode, 20)
    numpageavance = request.GET.get('page')
    listeperiode = pagineavance.get_page(numpageavance)


    return render(request, 'gPersonnel/liste_avance_salaire.html',dict(avance_periode=listeperiode,ddebut=debut, dfin=fin, annee=annee, total_avance=total_avance, solde_dispo=soldec, query_string=query_string))



@action_requise('personnel_avance_salaire')
def editeravancesalaire(request, idavsal):
    
    avsal = AvanceSalaire.objects.get(id=idavsal)
    ans = AnneeScolaire.objects.all().order_by('id')

    context = {'avsal': avsal, 'moisavance': MOIS_CHOICES, 'annee': ans}

    return render(request, 'gPersonnel/modifier_avance_salaire.html', context)


@action_requise('personnel_avance_salaire')
def detailsavancesalaire(request, idavsal):
    avsal = AvanceSalaire.objects.get(id=idavsal)
    return render(request, 'gPersonnel/afficher_details_avance_salaire.html', dict(avsal=avsal))


@action_requise('personnel_avance_salaire')
def modifieravancesalaire(request, idavsal):

    montant = 0
    if request.method == 'POST':
        avsal = AvanceSalaire.objects.get(id=idavsal)
        montant = request.POST['montant_avance']
        ane = request.POST['annee_scolaire']
        ansc = AnneeScolaire.objects.get(id=ane)

        avsal.montant_avance = Decimal(montant)
        avsal.intitule = request.POST['intitule']
        avsal.mois_avance = request.POST['mois_avance']
        avsal.date_avance = request.POST['date_avance']
        avsal.anscolaire = ansc
        avsal.save()

        return redirect('../listeavancemensuelle/')
    else:
        return redirect('../listeavancemensuelle/')


@action_requise('personnel_avance_salaire')
def supprimeravancesalaire(request, pk):
    avsal = AvanceSalaire.objects.get(id=pk)
    avsal.delete()
    return redirect('../listeavancemensuelle/')


# Impression de la liste des employés : Liste générale et par catégorie/type personnel (Vacataire ou Permanent)



# Impression du bon d'avance sur salaire
@action_requise('personnel_avance_salaire')
def recubonavancesalaire(request, idavance):

    mont_avance = ''
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

    # Ici je tente de recuperer les données sur l'avance de salaire depuis la BD

    avce = AvanceSalaire.objects.select_related('idpersonnel', 'anscolaire').get(id=idavance)
    data = [avce.id, avce.anscolaire.descript_annee, avce.idpersonnel.id, avce.idpersonnel.nom_personnel,
            avce.idpersonnel.prenom_personnel, avce.idpersonnel.fonction_personnel, avce.idpersonnel.contact_personnel, avce.get_mois_avance_display(), avce.date_avance,
            ]

    mont_avance = '{:,} GNF'.format(avce.montant_avance)
    date_avance_fmt = data[8].strftime('%d/%m/%Y') if hasattr(data[8], 'strftime') else str(data[8])
    

    ch = str(data[1]).split('-')  # "2023-2024" -> ['2023', '2024']
    ane = ch[1] if len(ch) > 1 else ''

    numrecu = data[0]
    ansco = datetime.now().strftime('%y')
    numero_recu = ''
    if numrecu < 10:
        numero_recu = ansco + '00' + str(numrecu)
    elif numrecu < 100:
        numero_recu = ansco + '0' + str(numrecu)
    elif numrecu < 1000:
        numero_recu = ansco + '0' + str(numrecu)
    elif numrecu < 10000:
        numero_recu = ansco + '0' + str(numrecu)

    num_emp = data[2]
    id_emp = ''
    if num_emp < 10:
        id_emp = ansco + '00' + str(num_emp)
    elif num_emp < 100:
        id_emp = ansco + '0' + str(num_emp)
    elif num_emp < 1000:
        id_emp = ansco + '0' + str(num_emp)
    elif num_emp < 10000:
        id_emp = ansco + '0' + str(num_emp)


    # --- Découpage de la description en lignes pour qu'elle tienne dans sa colonne ---
    # (le tableau est dessiné à la main avec drawString, qui ne retourne jamais la ligne
    # tout seul ; simpleSplit calcule les coupures selon la largeur réelle de la police)
    LARGEUR_COL_DESCRIPTION = 290   # largeur utile de la colonne (300pt de colonne - marges)
    FONT_DESCRIPTION = 'Helvetica'
    TAILLE_DESCRIPTION = 8
    HAUTEUR_LIGNE = 9
    HAUTEUR_LIGNE_BASE = 20         # hauteur d'une ligne de tableau à une seule ligne de texte
    MAX_LIGNES_DESCRIPTION = 3      # au-delà, la marge disponible ne suffit plus : on tronque

    lignes_description = simpleSplit(str(avce.intitule), FONT_DESCRIPTION, TAILLE_DESCRIPTION, LARGEUR_COL_DESCRIPTION)
    if not lignes_description:
        lignes_description = ['']
    if len(lignes_description) > MAX_LIGNES_DESCRIPTION:
        lignes_description = lignes_description[:MAX_LIGNES_DESCRIPTION]
        lignes_description[-1] = lignes_description[-1][:-1].rstrip() + '…'
    # Hauteur de la ligne de données : grandit uniquement vers le bas, dans l'espace
    # déjà disponible avant "Conakry, le" (aucun autre élément du reçu ne bouge).
    hauteur_ligne_donnees = max(HAUTEUR_LIGNE_BASE, 6 + len(lignes_description) * HAUTEUR_LIGNE)

    # --- Construction du PDF ---
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setTitle('Reçu Avance sur Salaire')

    def draw_recu(y_offset):
        """Dessine un reçu complet. y_offset=0 pour le haut, -420 pour le bas."""

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
            p.drawString(245, 770 + y_offset, str(data_ecole[5]))

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
        p.setFont('Helvetica-Bold', 11)
        p.drawString(330, 700 + y_offset, 'Session : ')
        p.setFont('Helvetica', 11)
        p.drawString(385, 700 + y_offset, str(ane))

        # ── TITRE RECU ──
        p.setFont('Helvetica-Bold', 12)
        p.rect(150, 673 + y_offset, 280, 18, stroke=True, fill=False)
        p.drawString(165, 677 + y_offset, f'RECU AVANCE/SALAIRE N° {numero_recu}')

        # ── INFOS EMPLOYE (gauche) ──
        p.setFont('Helvetica-Bold', 11)
        p.drawString(120, 650 + y_offset, 'ID Employé :')
        p.setFont('Helvetica', 11)
        p.drawString(195, 650 + y_offset, str(id_emp))

        p.setFont('Helvetica-Bold', 11)
        p.drawString(120, 634 + y_offset, 'Nom :')
        p.setFont('Helvetica', 11)
        p.drawString(195, 634 + y_offset, str(data[3]))

        p.setFont('Helvetica-Bold', 11)
        p.drawString(120, 618 + y_offset, 'Prénoms :')
        p.setFont('Helvetica', 11)
        p.drawString(195, 618 + y_offset, str(data[4]))

        p.setFont('Helvetica-Bold', 11)
        p.drawString(120, 600 + y_offset, 'Fonction :')
        p.setFont('Helvetica', 11)
        p.drawString(195, 600 + y_offset, str(data[5]))

        # ── INFOS EMPLOYE (droite) ──
        p.setFont('Helvetica-Bold', 11)
        p.drawString(340, 634 + y_offset, 'Contact :')
        p.setFont('Helvetica', 11)
        p.drawString(395, 634 + y_offset, str(data[6]))

        p.setFont('Helvetica-Bold', 11)
        p.drawString(340, 618 + y_offset, 'Mois de :')
        p.setFont('Helvetica', 11)
        p.drawString(395, 618 + y_offset, str(data[7]).capitalize())

        # ── TABLEAU DESCRIPTION / MONTANT / DATE ──
        # Largeurs ajustées : Description plus large, Montant avancé et Date paie resserrées
        # sur leur contenu réel. Total = 500 points (mêmes bornes que le reçu de scolarité).
        # L'en-tête reste à sa position fixe (555-575) ; seule la ligne de données
        # s'étend vers le bas, dans l'espace déjà disponible avant "Conakry, le" (510) —
        # rien d'autre dans le reçu ne se déplace, donc le 2e exemplaire ne peut jamais
        # déborder de la page.
        col_x = [20, 320, 430, 520]  # Description=300, Montant avancé=110, Date paie=90
        haut_entete = 575 + y_offset
        bas_entete = 555 + y_offset
        bas_donnees = bas_entete - hauteur_ligne_donnees

        # En-tête avec fond bleu et texte blanc
        p.setFillColor(colors.HexColor('#2980b9'))
        p.rect(20, bas_entete, 500, 20, stroke=True, fill=True)
        p.setFillColor(colors.white)
        p.setFont('Helvetica-Bold', 10)
        p.drawString(25, bas_entete + 5, 'Description opération')
        p.drawString(325, bas_entete + 5, 'Montant avancé')
        p.drawString(435, bas_entete + 5, 'Date paie')

        # Ligne de données — hauteur variable, la description peut tenir sur plusieurs lignes
        p.setFillColor(colors.black)
        p.setFont(FONT_DESCRIPTION, TAILLE_DESCRIPTION)
        p.rect(20, bas_donnees, 500, hauteur_ligne_donnees, stroke=True, fill=False)

        y_texte = bas_entete - 13
        for ligne in lignes_description:
            p.drawString(25, y_texte, ligne)
            y_texte -= HAUTEUR_LIGNE
        p.drawString(325, bas_entete - 13, mont_avance)
        p.drawString(435, bas_entete - 13, date_avance_fmt)

        # Lignes verticales du tableau (englobent l'en-tête ET les données)
        for x in col_x:
            p.line(x, bas_donnees, x, haut_entete)

        # ── DATE ET SIGNATURE ──
        # "Conakry, le" rapproché de la ligne Bénéficiaire/poste du signataire (22pt au lieu
        # de 35pt), puis le nom du signataire gardé à distance raisonnable en dessous (30pt,
        # pas collé) — position fixe, inchangée quelle que soit la hauteur du tableau ci-dessus.
        p.setFont('Helvetica-Bold', 11)
        p.drawString(375, 510 + y_offset, 'Conakry, le ')
        p.drawString(450, 510 + y_offset, datetime.now().strftime('%d/%m/%Y'))
        p.drawString(120, 488 + y_offset, 'Le Bénéficiaire')
        p.drawString(375, 488 + y_offset, 'Le Service Scolarité')
        p.drawString(375, 458 + y_offset, str(data_ecole[8]))

    # ── PREMIER EXEMPLAIRE ──
    draw_recu(0)

    # ── LIGNE SEPARATRICE ENTRE LES DEUX EXEMPLAIRES ──
    p.line(20, 420, 580, 420)

    # ── DEUXIEME EXEMPLAIRE ──
    draw_recu(-420)

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename='Bon_Avance_Salaire_' + str(id_emp) + '.pdf',content_type='application/pdf')


# Fonction de génération du bulletin de salaire

TYPE_VACATAIRE = TYPE_PERSONNEL[0][0]

# ---------------------------------------------------------------- Palette
NAVY = colors.HexColor("#1F3864")
GOLD = colors.HexColor("#C9A227")
GRAY_BG = colors.HexColor("#F2F2F2")
GRAY_MED = colors.HexColor("#595959")
GREEN_TOTAL = colors.HexColor("#E2EFDA")
RED_TOTAL = colors.HexColor("#FCE4E4")
WHITE = colors.white
BORDER = colors.HexColor("#BFBFBF")

STYLES = getSampleStyleSheet()

# NB : "leading" (interligne) est indispensable. Sans lui, ReportLab garde 12 pt
# par défaut et un titre en 16 pt chevauche la ligne suivante.
STYLE_TITLE = ParagraphStyle(
    "BulletinTitle", parent=STYLES["Normal"], fontName="Helvetica-Bold",
    fontSize=18, leading=22, spaceAfter=3, textColor=WHITE, alignment=TA_CENTER,
)
STYLE_SUBTITLE = ParagraphStyle(
    "BulletinSubtitle", parent=STYLES["Normal"], fontName="Helvetica-Oblique",
    fontSize=9.5, leading=13, spaceAfter=1, textColor=WHITE, alignment=TA_CENTER,
)
STYLE_SECTION = ParagraphStyle(
    "BulletinSection", parent=STYLES["Normal"], fontName="Helvetica-Bold",
    fontSize=10, textColor=WHITE, leftIndent=4,
)
STYLE_LABEL = ParagraphStyle(
    "BulletinLabel", parent=STYLES["Normal"], fontName="Helvetica-Bold",
    fontSize=9, textColor=GRAY_MED,
)
STYLE_LABEL_HEAD = ParagraphStyle(
    "BulletinLabelHead", parent=STYLE_LABEL, textColor=WHITE,
)
STYLE_VALUE = ParagraphStyle(
    "BulletinValue", parent=STYLES["Normal"], fontName="Helvetica",
    fontSize=9, textColor=colors.black,
)
STYLE_MONTANT = ParagraphStyle(
    "BulletinMontant", parent=STYLE_VALUE, alignment=TA_RIGHT,
)
STYLE_MONTANT_HEAD = ParagraphStyle(
    "BulletinMontantHead", parent=STYLE_LABEL_HEAD, alignment=TA_RIGHT,
)
STYLE_NET = ParagraphStyle(
    "BulletinNet", parent=STYLES["Normal"], fontName="Helvetica-Bold",
    fontSize=14, textColor=WHITE,
)
STYLE_NET_MONTANT = ParagraphStyle(
    "BulletinNetMontant", parent=STYLE_NET, alignment=TA_RIGHT,
)
STYLE_FOOTER = ParagraphStyle(
    "BulletinFooter", parent=STYLES["Normal"], fontName="Helvetica-Oblique",
    fontSize=7, textColor=colors.HexColor("#A6A6A6"), alignment=TA_CENTER,
)
# Légendes de signature : gras, noir, sans italique, lisibles
STYLE_SIGNATURE_G = ParagraphStyle(
    "BulletinSignatureG", parent=STYLES["Normal"], fontName="Helvetica-Bold",
    fontSize=10, leading=13, textColor=colors.black, alignment=TA_LEFT,
)
STYLE_SIGNATURE_D = ParagraphStyle(
    "BulletinSignatureD", parent=STYLE_SIGNATURE_G, alignment=TA_RIGHT,
)


# ---------------------------------------------------------------- Utilitaires
def _nombre(valeur):
    """Convertit une valeur (Decimal, float, None, str) en float, 0 si invalide."""
    if valeur is None:
        return 0.0
    try:
        return float(valeur)
    except (TypeError, ValueError):
        return 0.0


def formater_montant(valeur, devise=""):
    """Formate en '1 234 567 GNF' (séparateur espace, 0 décimale)."""
    texte = f"{_nombre(valeur):,.0f}".replace(",", " ")
    return f"{texte} {devise}".strip()


def _image_ou_none(fichier, largeur, hauteur):
    """Retourne un Image si le FileField pointe vers un fichier présent, sinon None."""
    if not fichier:
        return None
    try:
        chemin = fichier.path
        if os.path.exists(chemin):
            return Image(chemin, width=largeur, height=hauteur)
    except Exception:
        pass
    return None


def _bandeau_section(titre, largeur_page):
    t = Table([[Paragraph(titre, STYLE_SECTION)]], colWidths=[largeur_page])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _tableau_montants(lignes, libelle_total, fond_total, largeur_page):
    """
    Tableau Libellé / Montant avec une ligne de total en dernière position.
    lignes : liste de (libellé, montant_formaté) ; libelle_total : (libellé, montant_formaté).
    """
    data = [[Paragraph("Description", STYLE_LABEL_HEAD), Paragraph("Montant", STYLE_MONTANT_HEAD)]]
    for lbl, montant in lignes:
        data.append([Paragraph(lbl, STYLE_VALUE), Paragraph(montant, STYLE_MONTANT)])
    data.append([
        Paragraph(f"<b>{libelle_total[0]}</b>", STYLE_VALUE),
        Paragraph(f"<b>{libelle_total[1]}</b>", STYLE_MONTANT),
    ])
    t = Table(data, colWidths=[largeur_page * 0.7, largeur_page * 0.3])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GRAY_MED),
        ("BACKGROUND", (0, -1), (-1, -1), fond_total),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [WHITE, GRAY_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


# ---------------------------------------------------------------- Génération
def generer_bulletin_salaire(salaire, ecole=None, devise="GNF"):
    """
    Génère le bulletin de paie (PDF) d'un enregistrement Salaire.

    Paramètres
    ----------
    salaire : instance de Salaire (idpersonnel et anneescolaire liés)
    ecole   : instance de Ecole ; si None, Ecole.objects.first()
    devise  : libellé monétaire affiché après les montants (ex. "GNF").
              `devise_ecole` est le slogan de l'école, pas la monnaie.

    Retour
    ------
    BytesIO positionné au début, prêt pour une HttpResponse ou un email.
    """

    if ecole is None:
        ecole = Ecole.objects.first()

    personnel = salaire.idpersonnel
    est_vacataire = personnel.type_personnel == TYPE_VACATAIRE

    # ------------------------------------------------ Calculs d'affichage
    nbre_heure = salaire.nbre_heure if salaire.nbre_heure is not None else 0
    taux_horaire = _nombre(salaire.taux_horaire)
    avance = _nombre(salaire.avance_paie)
    cotisation = _nombre(salaire.cotis_sociale)

    if est_vacataire:
        base = nbre_heure * taux_horaire
        libelle_base = (
            f"Salaire de base ({nbre_heure} h × {formater_montant(taux_horaire, devise)})"
        )
    else:
        base = _nombre(personnel.salbase)
        libelle_base = "Salaire de base"

    # ------------------------------------------------ Document
    buffer = io.BytesIO()
    doc = BaseDocTemplate(
        buffer, pagesize=A4,
        topMargin=15 * mm, bottomMargin=15 * mm,
        leftMargin=15 * mm, rightMargin=15 * mm,
        title="Bulletin Salaire Mensuel",   # remplace le titre par défaut « (anonymous) »
        author=getattr(ecole, "nom_ecole", None) or "École",
        subject="Bulletin de Paie",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="bulletin", frames=[frame])])

    story = []
    largeur_page = doc.width

    # ============================================================ EN-TÊTE ÉCOLE
    logo = _image_ou_none(getattr(ecole, "logo_ecole", None), 18 * mm, 18 * mm) if ecole else None
    nom_ecole = getattr(ecole, "nom_ecole", None) or "École"
    telephone = getattr(ecole, "telephone1", None)
    coords_ecole = " • ".join(filter(None, [
        getattr(ecole, "ville_ecole", None),
        f"Tél : {telephone}" if telephone else None,
        getattr(ecole, "email_ecole", None),
    ]))

    entete_droite = [Paragraph(nom_ecole.upper(), STYLE_TITLE)]
    slogan = getattr(ecole, "devise_ecole", None)
    if slogan:
        entete_droite.append(Paragraph(f"« {slogan} »", STYLE_SUBTITLE))
    if coords_ecole:
        entete_droite.append(Paragraph(coords_ecole, STYLE_SUBTITLE))

    if logo:
        entete_table = Table(
            [[logo, entete_droite]],
            colWidths=[22 * mm, largeur_page - 22 * mm],
        )
    else:
        entete_table = Table([[entete_droite]], colWidths=[largeur_page])
    entete_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(entete_table)

    # Bandeau doré : interligne réduit à 16 pt (sinon il hériterait des 22 pt du titre)
    titre_table = Table(
        [[Paragraph("BULLETIN DE PAIE", ParagraphStyle(
            "titre2", parent=STYLE_TITLE, textColor=NAVY, fontSize=13, leading=16,
            spaceAfter=0))]],
        colWidths=[largeur_page],
    )
    titre_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(titre_table)
    story.append(Spacer(1, 6 * mm))

    # ============================================================ PÉRIODE
    date_paiement = (
        salaire.date_paiement.strftime("%d/%m/%Y") if salaire.date_paiement else ""
    )
    periode_table = Table([[
        Paragraph(f"<b>Période :</b> {salaire.get_mois_paie_display().capitalize()} — {salaire.anneescolaire}",
                  STYLE_VALUE),
        Paragraph(f"<b>Date de paiement :</b> {date_paiement}", STYLE_VALUE),
    ]], colWidths=[largeur_page / 2, largeur_page / 2])
    periode_table.setStyle(TableStyle([("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.append(periode_table)
    story.append(Spacer(1, 3 * mm))

    # ============================================================ SECTION EMPLOYÉ
    story.append(_bandeau_section("INFORMATIONS DE L'EMPLOYÉ", largeur_page))
    story.append(Spacer(1, 2 * mm))

    civilite = (
        personnel.get_civilite_display()
        if hasattr(personnel, "get_civilite_display") else personnel.civilite
    )
    infos = [
        ("Nom & Prénom", f"{civilite} {personnel.nom_personnel} {personnel.prenom_personnel}",
         "Fonction", personnel.fonction_personnel or "—"),
        ("Type de personnel", personnel.get_type_personnel_display(),
         "Type de contrat", personnel.get_contrat_type_display()),
        ("Date d'embauche",
         personnel.date_embauche.strftime("%d/%m/%Y") if personnel.date_embauche else "—",
         "Année d'expérience", personnel.annee_experience or "—"),
        ("Contact", personnel.contact_personnel or "—",
         "Situation matrimoniale", personnel.get_etat_matrimonial_display()),
    ]
    data_infos = []
    for l1, v1, l2, v2 in infos:
        data_infos.append([
            Paragraph(l1, STYLE_LABEL), Paragraph(str(v1), STYLE_VALUE),
            Paragraph(l2, STYLE_LABEL), Paragraph(str(v2), STYLE_VALUE),
        ])
    largeur_col = largeur_page / 4
    t_infos = Table(data_infos, colWidths=[largeur_col] * 4)
    t_infos.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), GRAY_BG),
        ("BACKGROUND", (2, 0), (2, -1), GRAY_BG),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_infos)
    story.append(Spacer(1, 4 * mm))

    # ============================================================ RÉMUNÉRATION
    story.append(_bandeau_section("ÉLÉMENTS DE RÉMUNÉRATION", largeur_page))
    story.append(Spacer(1, 2 * mm))

    lignes_remu = [
        (libelle_base, formater_montant(base, devise)),
        ("Primes", formater_montant(salaire.primes, devise)),
    ]
    if (salaire.nb_hsupp or 0) or _nombre(salaire.mont_hsupp):
        lignes_remu.append((
            f"Heures supplémentaires ({salaire.nb_hsupp or 0} h)",
            formater_montant(salaire.mont_hsupp, devise),
        ))

    # Les avances sont déduites du brut (salbrut stocké = base + primes + h. supp - avances)
    lignes_remu.append((
        "Avances sur salaire (−)",
        "− " + formater_montant(avance, devise),
    ))

    story.append(_tableau_montants(
        lignes_remu,
        ("SALAIRE BRUT", formater_montant(salaire.salbrut, devise)),
        GREEN_TOTAL, largeur_page,
    ))
    story.append(Spacer(1, 4 * mm))

    # ============================================================ RETENUES
    story.append(_bandeau_section("RETENUES SUR SALAIRE", largeur_page))
    story.append(Spacer(1, 2 * mm))

    lignes_ret = [
        ("Cotisation sociale", formater_montant(cotisation, devise)),
    ]
    story.append(_tableau_montants(
        lignes_ret,
        ("TOTAL RETENUES", formater_montant(cotisation, devise)),
        RED_TOTAL, largeur_page,
    ))
    story.append(Spacer(1, 5 * mm))

    # ============================================================ NET À PAYER
    net_table = Table([[
        Paragraph("NET À PAYER", STYLE_NET),
        Paragraph(f"<b>{formater_montant(salaire.salnet, devise)}</b>", STYLE_NET_MONTANT),
    ]], colWidths=[largeur_page * 0.5, largeur_page * 0.5])
    net_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(net_table)
    story.append(Spacer(1, 4 * mm))

    if salaire.detail_paiement:
        story.append(Paragraph("<b>Détails :</b>", STYLE_LABEL))
        story.append(Paragraph(salaire.detail_paiement, STYLE_VALUE))
        story.append(Spacer(1, 4 * mm))

    # ============================================================ SIGNATURES
    story.append(Spacer(1, 8 * mm))
    signa_dg = (
        _image_ou_none(getattr(ecole, "signa_dg", None), 30 * mm, 15 * mm) if ecole else None
    )
    nom_dg = getattr(ecole, "dg", None)
    titre_dg = "Le Directeur Général" + (f" — {nom_dg}" if nom_dg else "")

    larg_sig = 80 * mm
    if signa_dg:
        signa_dg.hAlign = "RIGHT"
    sig_table = Table([
        [Paragraph("Signature de l'employé", STYLE_SIGNATURE_G), "",
         Paragraph(titre_dg, STYLE_SIGNATURE_D)],
        ["", "", signa_dg if signa_dg else ""],
    ], colWidths=[larg_sig, largeur_page - 2 * larg_sig, larg_sig],
        rowHeights=[None, 16 * mm])
    sig_table.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("ALIGN", (2, 1), (2, 1), "RIGHT"),
        ("LINEBELOW", (0, 1), (0, 1), 0.8, colors.black),
        ("LINEBELOW", (2, 1), (2, 1), 0.8, colors.black),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 6 * mm))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#D9D9D9")))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "Ce document est confidentiel et destiné uniquement à l'employé concerné.",
        STYLE_FOOTER,
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer

# vue qui appelle la fonction de génération du bulletin de paie
@action_requise('personnel_salaire')
def recubulletinsalaire(request, idsal):
    salaire = get_object_or_404(Salaire, pk=idsal)
    buffer = generer_bulletin_salaire(salaire)
    nom_fichier = f"Bulletin_Salaire_{salaire.idpersonnel.nom_personnel}_{salaire.idpersonnel.prenom_personnel}_{salaire.mois_paie}.pdf"

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{nom_fichier}"'
    return response
    

@action_requise('personnel_avance_salaire')
def imprimerecuavancesalaire(request, idavce):
    return HttpResponseRedirect(reverse('recuavancesalaire',
                                        args=(
                                            idavce,)))

@action_requise('personnel_salaire')
def imprimebulletinsalaire(request, idsal):
    return HttpResponseRedirect(reverse('recubulletinsalaire',
                                        args=(
                                            idsal,)))
