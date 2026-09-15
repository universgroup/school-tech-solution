from datetime import date
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from core.datatables_utils import *
from .models import *

# gEleve/views.py (ou colonnes.py)

COLUMNS_MAP_INSCRITS = [
    ('etat_inscription',              True,  True),   # 0  Statut
    ('mateleve__matricule',           True,  True),   # 1  Matricule
    ('mateleve__nom',                 True,  True),   # 2  Nom Famille
    ('mateleve__prenom',              True,  True),   # 3  Prénom(s)
    ('mateleve__sexe_eleve',          True,  True),   # 4  Sexe
    ('mateleve__pere',                True,  True),   # 5  Prénom(s) Père
    ('mateleve__mere',                True,  True),   # 6  Prénom(s) & Nom Mère
    ('mateleve__tuteur',              True,  True),   # 7  Prénom(s) & Nom Tuteur
    ('mateleve__contact_pere',        True,  True),   # 8  Contact père
    ('mateleve__contact_mere',        True,  True),   # 9  Contact mère
    ('mateleve__email_pere',          True,  True),   # 10 Email père
    ('mateleve__email_mere',          True,  True),   # 11 Email mère
    ('mateleve__profes_pere',         True,  True),   # 12 Profession père
    ('mateleve__profes_mere',         True,  True),   # 13 Profession mère
    ('mateleve__personne_contact',    True,  True),   # 14 Personne contact
    ('mateleve__adresse',             True,  True),   # 15 Adresse
    ('mateleve__ecole_origine',       True,  True),   # 16 Ecole d'origine
    (None,                            False, False),  # 17 Photo ID
    ('mateleve__datenaissance',       True,  True),   # 18 Date naissance
    ('mateleve__lieu_naissance',      True,  True),   # 19 Lieu naissance
    ('mateleve__date_arrivee',        True,  True),   # 20 Date entrée
    ('mateleve__pays_naissance',      True,  True),   # 21 Pays naissance
    ('idclasse__nom_classe',          True,  True),   # 22 Classe
    ('idcycle__cycle',                True,  True),   # 23 Cycle  ⚠️ champ à confirmer
    ('annee_scolaire__descript_annee',True,  True),   # 24 Année scolaire ⚠️ champ à confirmer
    ('date_inscription',              True,  True),   # 25 Date inscription
    ('id',                            True,  True),   # 26 ID Inscription
    (None,                            False, False),  # 27 Actions
]

CHAMPS_RECHERCHE_GLOBALE = [
    'mateleve__matricule', 'mateleve__nom', 'mateleve__prenom',
    'mateleve__contact_pere', 'mateleve__contact_mere',
]


# Fonction commune de rendu des lignes (évite la duplication entre les deux vues)
def construire_ligne_json(inscription, ok_admin):
    eleve = inscription.mateleve

    if eleve.photo_eleve:
        photo_html = (
            f'<a href="{eleve.photo_eleve.url}" target="_blank" title="Agrandir la photo de l\'élève">'
            f'<img src="{eleve.photo_eleve.url}" width="40px"></a>'
        )
    else:
        photo_html = "Photo indisponible"

    actions_html = (
        f'<a class="btn btn-primary" href="{reverse("afficherdetailsinscription", args=[inscription.id])}" title="Voir/Afficher"><i class="fa fa-eye fa-sm"></i></a> '
        f'<a class="btn btn-info" href="{reverse("editioninscription", args=[inscription.id])}" title="Modifier/Editer"><i class="fa fa-edit fa-sm"></i></a> '
    )
    if ok_admin:
        actions_html += (
            f'<a class="btn btn-danger" href="{reverse("suppinscription", args=[inscription.id])}" title="Supprimer"><i class="fa fa-remove fa-sm"></i></a> '
        )
    actions_html += (
        f'<a class="btn btn-secondary" target="_blank" href="{reverse("imprimerecuinscription", args=[inscription.id])}" title="Imprimer le reçu d\'inscription"><i class="fa fa-print fa-sm"></i></a> '
        f'<a class="btn btn-dark" target="_blank" href="{reverse("imprimerbadgeeleve", args=[inscription.id])}" title="Imprimer le badge de l\'élève"><i class="fas fa-id-card fa-sm"></i></a>'
    )

    return [
        inscription.etat_inscription,
        eleve.matricule,
        eleve.nom,
        eleve.prenom,
        eleve.sexe_eleve,
        eleve.pere,
        eleve.mere,
        eleve.tuteur,
        eleve.contact_pere,
        eleve.contact_mere,
        eleve.email_pere,
        eleve.email_mere,
        eleve.profes_pere,
        eleve.profes_mere,
        eleve.personne_contact,
        eleve.adresse,
        eleve.ecole_origine,
        photo_html,
        eleve.datenaissance.strftime('%d-%m-%Y') if eleve.datenaissance else '',
        eleve.lieu_naissance,
        eleve.date_arrivee.strftime('%d-%m-%Y') if eleve.date_arrivee else '',
        eleve.pays_naissance,
        str(inscription.idclasse),
        str(inscription.idcycle),
        str(inscription.annee_scolaire),
        inscription.date_inscription.strftime('%d-%m-%Y') if inscription.date_inscription else '',
        inscription.id,
        actions_html,
    ]

# 4. Vue AJAX n°1 — équivalent de listeinscritsanneescolairecourante (liste mensuelle)

def ajax_liste_inscrits_mois(request):
    params = parse_datatables_params(request, COLUMNS_MAP_INSCRITS)

    mois_actuel = date.today().strftime('%m')

    queryset = Inscription.objects.select_related(
        'annee_scolaire', 'mateleve', 'idcycle', 'idclasse'
    ).filter(
        etat_inscription__exact=ETAT_INSCRIPTION[0][1],
        date_inscription__month=mois_actuel,
    )

    total_avant_filtre = queryset.count()

    queryset = appliquer_recherches_colonnes(queryset, params['column_searches'])
    queryset = appliquer_recherche_globale(queryset, params['search_value'], CHAMPS_RECHERCHE_GLOBALE)

    # Effectifs calculés sur le filtré (avant pagination), sans variables globales
    effectif_total = queryset.count()
    effectif_total_garcons = queryset.filter(mateleve__sexe_eleve=SEXE_ELEVE_CHOICES[1][0]).count()
    effectif_total_filles = queryset.filter(mateleve__sexe_eleve=SEXE_ELEVE_CHOICES[2][0]).count()

    queryset = appliquer_tri(queryset, params['order_field'], params['order_dir'])
    queryset = queryset.order_by(*queryset.query.order_by) if params['order_field'] else queryset.order_by('-date_inscription')

    page = queryset[params['start']:params['start'] + params['length']]

    ok_admin = request.user.has_perm('menu_administration') if hasattr(request.user, 'has_perm') else False
    data = [construire_ligne_json(insc, ok_admin) for insc in page]

    return JsonResponse({
        'draw': params['draw'],
        'recordsTotal': total_avant_filtre,
        'recordsFiltered': effectif_total,
        'data': data,
        'effectif_total': effectif_total,
        'effectif_total_garcons': effectif_total_garcons,
        'effectif_total_filles': effectif_total_filles,
    })


# 5. Vue AJAX n°2 — équivalent de filtrelisteinscrits (filtre classe/cycle/année)

def ajax_liste_inscrits_filtre(request):
    params = parse_datatables_params(request, COLUMNS_MAP_INSCRITS)

    idclass = request.GET.get('id_classe')
    idcy = request.GET.get('cycle')
    idansc = request.GET.get('annee_scolaire')

    if not (idclass and idcy and idansc):
        return JsonResponse({
            'draw': params['draw'], 'recordsTotal': 0, 'recordsFiltered': 0, 'data': [],
            'effectif_total': 0, 'effectif_total_garcons': 0, 'effectif_total_filles': 0,
        })

    queryset = Inscription.objects.select_related(
        'annee_scolaire', 'mateleve', 'idcycle', 'idclasse'
    ).filter(
        idclasse__exact=idclass,
        idcycle__exact=idcy,
        annee_scolaire__exact=idansc,
        etat_inscription__exact=ETAT_INSCRIPTION[0][1],
    )

    total_avant_filtre = queryset.count()

    queryset = appliquer_recherches_colonnes(queryset, params['column_searches'])
    queryset = appliquer_recherche_globale(queryset, params['search_value'], CHAMPS_RECHERCHE_GLOBALE)

    effectif_total = queryset.count()
    effectif_total_garcons = queryset.filter(mateleve__sexe_eleve=SEXE_ELEVE_CHOICES[1][0]).count()
    effectif_total_filles = queryset.filter(mateleve__sexe_eleve=SEXE_ELEVE_CHOICES[2][0]).count()

    queryset = appliquer_tri(queryset, params['order_field'], params['order_dir']) if params['order_field'] else queryset.order_by('-date_inscription')

    page = queryset[params['start']:params['start'] + params['length']]

    ok_admin = request.user.has_perm('menu_administration') if hasattr(request.user, 'has_perm') else False
    data = [construire_ligne_json(insc, ok_admin) for insc in page]

    return JsonResponse({
        'draw': params['draw'],
        'recordsTotal': total_avant_filtre,
        'recordsFiltered': effectif_total,
        'data': data,
        'effectif_total': effectif_total,
        'effectif_total_garcons': effectif_total_garcons,
        'effectif_total_filles': effectif_total_filles,
    })