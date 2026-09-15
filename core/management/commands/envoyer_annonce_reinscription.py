from django.core.management.base import BaseCommand
from datetime import datetime
from core.emailing import envoyer_emails_masse
# from core.sms import envoyer_sms_masse

from gAdministration.models import Ecole
from gEleve.models import Eleve


class Command(BaseCommand):
    help = "Envoie automatiquement l'annonce de réouverture des réinscriptions le jour J"

    def handle(self, *args, **options):
        aujourdhui = datetime.now().date()
        self.stdout.write(f"[Annonce réinscription] Vérification au {aujourdhui}")

        ecole = Ecole.objects.first()
        if not ecole or not ecole.delai_reinscription:
            self.stdout.write("Aucune date de réinscription configurée.")
            return

        if ecole.delai_reinscription != aujourdhui:
            self.stdout.write(f"Ce n'est pas encore le jour des reinscriptions configuré : {ecole.delai_reinscription}).")
            return

        eleves = Eleve.objects.all()   # tous les élèves, puisque la date est globale à l'école, pas par année
        self.stdout.write(f"{eleves.count()} élève(s) concerné(s).")

        destinataires = []
        # destinataires_sms = []

        for eleve in eleves:
            contexte = {
                'nom_eleve': f"{eleve.prenom} {eleve.nom}",
                'date_ouverture': ecole.delai_reinscription.strftime('%d/%m/%Y'),
                'ire': ecole.ville_ecole,
                'bp': ecole.bp_ecole,
                'contact': f"{ecole.telephone1}/{ecole.telephone2}",
                'email_ecole': ecole.email_ecole,
                'texte_brut': f"Les réinscriptions ouvrent aujourd'hui, {ecole.delai_reinscription.strftime('%d/%m/%Y')}.",
            }
            if eleve.email_pere:
                destinataires.append((eleve.email_pere, contexte))
            if eleve.email_mere and eleve.email_mere != eleve.email_pere:
                destinataires.append((eleve.email_mere, contexte))

            # contexte_sms = {                                                    
            #     'nom_eleve': f"{eleve.prenom} {eleve.nom}",                      
            #     'nom_ecole': ecole.nom_ecole,                                    
            #     'date_ouverture': ecole.delai_reinscription.strftime('%d/%m/%Y'),
            # }           
            # if eleve.telephone_pere:                                          
            #     destinataires_sms.append((eleve.telephone_pere, contexte_sms)) 
            # if eleve.telephone_mere and eleve.telephone_mere != eleve.telephone_pere: 
            #     destinataires_sms.append((eleve.telephone_mere, contexte_sms))


        envoyes, echecs = envoyer_emails_masse(
            destinataires,
            'emails/annonce_reinscription.html',
            sujet="Ouverture des réinscriptions"
        )

        self.stdout.write(self.style.SUCCESS(f"{envoyes} email(s) envoyé(s), {echecs} échec(s)."))

        # template_sms = (                                                        
        #     "{nom_ecole} : les reinscriptions pour {nom_eleve} ouvrent "  
        #     "le {date_ouverture}. Merci de vous rapprocher du service scolarite."  
        # )                                                                       
        # envoyes_sms, echecs_sms = envoyer_sms_masse(destinataires_sms, template_sms)  

        # self.stdout.write(self.style.SUCCESS(f"{envoyes_sms} SMS envoyé(s), {echecs_sms} échec(s).")) 

