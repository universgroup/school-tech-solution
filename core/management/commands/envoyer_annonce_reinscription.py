from django.core.management.base import BaseCommand
from datetime import datetime
from core.emailing import envoyer_emails_masse
from gAdministration.models import Ecole
from gEleve.models import Eleve


class Command(BaseCommand):
    help = "Envoie automatiquement l'annonce de réouverture des réinscriptions le jour J"

    def handle(self, *args, **options):
        aujourdhui = datetime.now().date()

        ecole = Ecole.objects.first()
        if not ecole or not ecole.delai_reinscription:
            self.stdout.write("Aucune date de réinscription configurée.")
            return

        if ecole.delai_reinscription != aujourdhui:
            self.stdout.write("Ce n'est pas encore le jour de l'ouverture des réinscriptions.")
            return

        eleves = Eleve.objects.all()   # tous les élèves, puisque la date est globale à l'école, pas par année
        self.stdout.write(f"{eleves.count()} élève(s) concerné(s).")

        destinataires = []
        for eleve in eleves:
            contexte = {
                'nom_eleve': f"{eleve.prenom} {eleve.nom}",
                'date_ouverture': ecole.delai_reinscription.strftime('%d/%m/%Y'),
                'texte_brut': f"Les réinscriptions ouvrent aujourd'hui, {ecole.delai_reinscription.strftime('%d/%m/%Y')}.",
            }
            if eleve.email_pere:
                destinataires.append((eleve.email_pere, contexte))
            if eleve.email_mere and eleve.email_mere != eleve.email_pere:
                destinataires.append((eleve.email_mere, contexte))

        envoyes, echecs = envoyer_emails_masse(
            destinataires,
            'emails/annonce_reinscription.html',
            sujet="Ouverture des réinscriptions"
        )

        self.stdout.write(self.style.SUCCESS(f"{envoyes} email(s) envoyé(s), {echecs} échec(s)."))