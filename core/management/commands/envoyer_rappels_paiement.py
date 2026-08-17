from django.core.management.base import BaseCommand
from datetime import datetime, timedelta # timedelta est une classe qui permet de calculer la durée entre deux dates
from core.emailing import envoyer_emails_masse
from gAdministration.models import Ecole
from gComptabilite.models import EtatPaiementTranche

class Command(BaseCommand):
    help = "Envoie un rappel par email aux parents dont la date limite de paiement (tranche 1 ou 2) approche (7 jours)"

    def handle(self, *args, **options):
        aujourdhui = datetime.now().date()
        date_seuil = aujourdhui + timedelta(days=7)

        ecole = Ecole.objects.first()
        if not ecole:
            self.stdout.write(self.style.ERROR("Aucune information d'école configurée."))
            return

        # --- Tranche 1 ---
        if ecole.delai_tranche1 == date_seuil:
            self.envoyer_rappel_tranche(champ_paye='premiere_tranche', champ_montant='tranche1', nom_tranche_libelle="1ère tranche", date_limite=ecole.delai_tranche1)

        # --- Tranche 2 ---
        if ecole.delai_tranche2 == date_seuil:
            self.envoyer_rappel_tranche(champ_paye='deuxieme_tranche', champ_montant='tranche2', nom_tranche_libelle="2ème tranche", date_limite=ecole.delai_tranche2)


    def envoyer_rappel_tranche(self, champ_paye, champ_montant, nom_tranche_libelle, date_limite):
    # Toutes les données nécessaires en une seule requête (mateleve + idclasse pour le montant de la tranche)
        etatpaie = EtatPaiementTranche.objects.select_related('mateleve', 'idclasse')

        destinataires = []
        nb_concernes = 0

        for etat in etatpaie:
            eleve = etat.mateleve
            classe = etat.idclasse
            if not classe:
                continue

            montant_tranche = getattr(classe, champ_montant) or 0   # ex. classe.tranche1 ou classe.tranche2
            paye = getattr(etat, champ_paye) or 0  # ex. etat.premiere_tranche ou etat.deuxieme_tranche
            reste_tranche = montant_tranche - paye

            if reste_tranche <= 0:
                continue   # cette tranche est déjà entièrement soldée, pas de rappel nécessaire

            nb_concernes += 1
            contexte = {
                'nom_eleve': f"{eleve.prenom} {eleve.nom}",
                'classe': str(classe),
                'nom_tranche': nom_tranche_libelle,
                'reste_a_payer': '{:,}'.format(reste_tranche),
                'date_limite': date_limite.strftime('%d/%m/%Y'),
                'texte_brut': f"Rappel : la date limite de paiement de la {nom_tranche_libelle} est le {date_limite.strftime('%d/%m/%Y')}.",
            }
            if eleve.email_pere:
                destinataires.append((eleve.email_pere, contexte))
            if eleve.email_mere and eleve.email_mere != eleve.email_pere:
                destinataires.append((eleve.email_mere, contexte))

        self.stdout.write(f"{nb_concernes} élève(s) concerné(s) par le rappel {nom_tranche_libelle}.")

        envoyes, echecs = envoyer_emails_masse(
            destinataires,
            'emails/rappel_paiement.html',
            sujet=f"Rappel : date limite de paiement — {nom_tranche_libelle}"
        )

        self.stdout.write(self.style.SUCCESS(f"{envoyes} email(s) envoyé(s), {echecs} échec(s) pour la {nom_tranche_libelle}."))