from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
import io
from django.http import FileResponse, HttpResponseRedirect, HttpResponse, JsonResponse
from reportlab.pdfgen import canvas

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors  # Contient les méthodes/fonctions de gestion des couleurs
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, NextPageTemplate,
    Table, TableStyle, Paragraph, Spacer)
from reportlab.platypus import Table as RLTable  # évite le conflit de nom avec votre "Table" du tableau principal
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT # TA_CENTER, 
from reportlab.lib.utils import ImageReader, simpleSplit
from django.utils.dateparse import parse_date

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
    base = emp.salbase if emp.type_personnel == 'Permanent' else 0

    return JsonResponse({
        'nom': emp.nom_personnel,
        'prenom': emp.prenom_personnel,
        'contact': emp.contact_personnel,
        'type_employe': emp.type_personnel,
        'salbase': float(base),
        'avances': float(avances),
    })

# Fonction permettant de convertir les valeurs numériques recupérées depuis le formulaire en Decimal
def to_decimal(valeur):
    """Convertit une valeur de formulaire en Decimal ('1 000,50' -> Decimal('1000.50'))."""
    if valeur is None:
        return Decimal('0')
    texte = str(valeur).replace('\xa0', '').replace(' ', '').replace(',', '.').strip()
    if texte == '':
        return Decimal('0')
    try:
        return Decimal(texte)
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

                sb = salb + Decimal(sal.primes) + Decimal(sal.mont_hsupp)
                sal.salbrut = sb
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

    total_salbase = 0
    total_primes = 0
    total_salbrut = 0
    total_avance = 0
    total_salnet = 0

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
    
    return render(request, 'gPersonnel/enregistrer_salaire.html', context)


@action_requise('personnel_salaire')
def editersalaire(request, idsal):
    sal = Salaire.objects.get(id=idsal)
    context = {'sal': sal}
    return render(request, 'gPersonnel/modifier_salaire.html', context)


@action_requise('personnel_salaire')
def detailssalaire(request, idsal):
    sal = Salaire.objects.get(id=idsal)
    return render(request, 'gPersonnel/afficher_details_salaire.html', dict(sal=sal))


@action_requise('personnel_salaire')
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
        return redirect('../ajoutersalaire/')
    else:
        return redirect('../ajoutersalaire/')


@action_requise('personnel_salaire')
def supprimersalaire(request, pk):
    sal = Salaire.objects.get(id=pk)
    sal.delete()
    return redirect('../ajoutersalaire/')


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


@action_requise('personnel_salaire')
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
