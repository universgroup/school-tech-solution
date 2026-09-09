from django.db.models import Sum, Count

from gComptabilite.models import EtatPaiementTranche
from gAdministration.models import Classe
from gEleve.models import Inscription


def get_progression_paiements(annee_encours):
    paiements_par_classe = (
        EtatPaiementTranche.objects
        .filter(anneescolaire__descript_annee__exact=annee_encours)
        .values('idclasse_id')
        .annotate(
            premiere_tranche=Sum('premiere_tranche'),
            deuxieme_tranche=Sum('deuxieme_tranche'),
        )
    )
    paiements_dict = {p['idclasse_id']: p for p in paiements_par_classe} # Permet de faire le cumul des paiements des différentes tranches par classe durant l'année scolaire encours (cle=p[idclasse_id]: valeur=p)

    # Permet de calculer l'effectif par classe durant l'année scolaire actuelle
    inscrits_par_classe = (
        Inscription.objects
        .filter(annee_scolaire__descript_annee__exact=annee_encours)
        .values('idclasse_id', 'idclasse__nom_classe')
        .annotate(nb_eleves=Count('id'))
        .order_by('idclasse_id')
    )

    frais_par_classe = {c.id: (c.frais_scolarite or 0) for c in Classe.objects.all()}

    progression_paiements = []
    for ligne in inscrits_par_classe:
        classe_id = ligne['idclasse_id']
        montant_attendu = frais_par_classe.get(classe_id, 0) * ligne['nb_eleves']

        paiement = paiements_dict.get(classe_id, {})
        premiere = paiement.get('premiere_tranche') or 0
        deuxieme = paiement.get('deuxieme_tranche') or 0
        montant_restant = montant_attendu - (premiere + deuxieme)

        progression_paiements.append({
            'nom_classe': ligne['idclasse__nom_classe'],
            'montant_attendu': montant_attendu,
            'premiere_tranche': premiere,
            'deuxieme_tranche': deuxieme,
            'montant_restant': montant_restant,
        })

    return progression_paiements

def get_totaux_paiements(progression_paiements):
    """Calcule les totaux à partir de la liste déjà construite par get_progression_paiements."""
    return {
        'montant_attendu': sum(l['montant_attendu'] for l in progression_paiements),
        'premiere_tranche': sum(l['premiere_tranche'] for l in progression_paiements),
        'deuxieme_tranche': sum(l['deuxieme_tranche'] for l in progression_paiements),
        'montant_restant': sum(l['montant_restant'] for l in progression_paiements),
    }