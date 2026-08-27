# gUsers/permissions.py
"""
Source unique de vérité pour les permissions par niveau d'accès.
Utilisé par :
- gUsers/decorators.py (blocage côté vue)
- gUsers/templatetags/permissions_tags.py (masquage côté template)
"""
from datetime import datetime

from .models import (
    DIRECTEUR_GENERAL as DG,
    SERVICE_SCOLARITE as SCOL,
    COMPTABLE as COMPTA,
    ENSEIGNANT as ENS,
)

# ---------------------------------------------------------------------------
# 1. Permissions statiques (menus, actions ne dépendant pas d'un objet précis)
# ---------------------------------------------------------------------------
PERMISSIONS = {
    # Menus
    "menu_administration": [DG],
    "menu_eleves": [DG, SCOL, COMPTA],
    "menu_comptabilite": [DG, SCOL ,COMPTA],
    "menu_personnel": [],
    "menu_evaluation": [],
    "menu_services": [],

    # Élèves
    "eleve_inscrire": [DG, SCOL, COMPTA],
    "eleve_modifier": [DG, SCOL, COMPTA],
    "eleve_supprimer": [DG],
    "voir_montants_paiement": [DG, COMPTA],

    # Comptabilité
    "compta_ajouter": [DG, SCOL, COMPTA],
    "compta_modifier": [DG, SCOL, COMPTA],
    "compta_annuler": [DG, COMPTA],
    "compta_supprimer": [DG],           
    "compta_cloturer_mois": [DG, COMPTA],

    # Personnel
    "personnel_gerer": [],

    # Évaluation
    "matiere_gerer": [],
    "periode_gerer": [],
    "bulletin_generer": [],
    "note_modifier": [],      # ENS : voir peut_modifier_note() ci-dessous

    # Services
    "services_gerer": [],
}


def peut(user, cle):
    """Vérifie une permission statique (menu ou action sans objet)."""
    return user.is_authenticated and user.niveau_acces in PERMISSIONS.get(cle, [])


# ---------------------------------------------------------------------------
# 2. Permissions dépendant d'un objet / d'une date (Évaluation)
# ---------------------------------------------------------------------------
def peut_saisir_note(user, periode):
    """
    DG et Service Scolarité : toujours autorisés.
    Enseignant : autorisé uniquement avant la date_limite_saisie de la période.
    """
    if not user.is_authenticated:
        return False
    if user.niveau_acces in (DG, SCOL):
        return True
    if user.niveau_acces == ENS:
        return datetime.now().date() <= periode.date_limite_saisie
    return False


def peut_modifier_note(user, note):
    return peut_saisir_note(user, note.periode)


# ---------------------------------------------------------------------------
# 3. Permissions dépendant d'un objet / d'une date (Comptabilité)
# ---------------------------------------------------------------------------
def peut_annuler_operation(user, operation):
    """
    DG et Comptable uniquement, et seulement si le mois de l'opération
    n'a pas déjà été clôturé.
    """
    if not user.is_authenticated or user.niveau_acces not in (DG, COMPTA):
        return False
    if operation.est_annulee:
        return False
    from gComptabilite.models import ClotureMensuelle
    mois_cloture = ClotureMensuelle.objects.filter(
        mois=operation.date_operation.month,
        annee=operation.date_operation.year,
    ).exists()
    return not mois_cloture


def peut_modifier_operation(user, operation):
    """
    Même règle que l'annulation : pas de correction sur un mois clôturé.
    """
    if not user.is_authenticated or user.niveau_acces not in (DG, COMPTA):
        return False
    if operation.est_annulee:
        return False
    from gComptabilite.models import ClotureMensuelle
    mois_cloture = ClotureMensuelle.objects.filter(
        mois=operation.date_operation.month,
        annee=operation.date_operation.year,
    ).exists()
    return not mois_cloture
