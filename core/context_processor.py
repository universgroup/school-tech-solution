from datetime import date
from gAdministration.models import Ecole

def annee_scolaire_actuelle(request):
    """
    Calcule dynamiquement l'année scolaire en cours selon la date système.
    Règle : l'année scolaire N débute le 01/09/N et se termine le 31/08/(N+1).
    """
    aujourdhui = date.today() # Je recupère la date actuelle
    annee = aujourdhui.year # Je recupère l'année de cette date i.e l'année encours
    mois = aujourdhui.month # Je recupère le mois de cette date i.e le mois actuel/encours

    if mois >= 9:  # Septembre à Décembre → nouvelle année scolaire démarrée
        debut = annee # Par exemple 2026
        fin = annee + 1 # Par exemple 2027
    else:  # Janvier à Août → on est encore dans l'année scolaire précédente
        debut = annee - 1 # Par exemple 2026
        fin = annee # Par exemple 2027

    return {
        'annee_scolaire': f"{debut}-{fin}", # 2026-2027
        'annee_scolaire_debut': debut,
        'annee_scolaire_fin': fin,
        'session_scolaire': fin # 2027
    }


def afficher_logoEcole(request):

    ecole = Ecole.objects.first()
    logo_ecole = None
    nom_ecole = None

    if ecole is not None:
        logo_ecole = ecole.logo_ecole
        nom_ecole = ecole.nom_ecole


    context = {'logo_ecole':logo_ecole,
               'nom_ecole': nom_ecole}

    return context






# def donnees_menu_rapports(request):

#     if not request.user.is_authenticated:
#         return {}
#     return {
#         'anneescol': AnneeScolaire.objects.all().order_by('id'),
#         'cyclescol': CycleScolaire.objects.all(),
#     }

