from django.core.management.base import BaseCommand
from datetime import datetime
from core.emailing import envoyer_emails_masse
from core.sms import envoyer_sms_masse, _client


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
        destinataires_sms = []
        eleves_sans_contact = []  

        for eleve in eleves:
            contexte = {
                'nom_eleve': f"{eleve.prenom} {eleve.nom}",
                'date_ouverture': ecole.delai_reinscription.strftime('%d/%m/%Y'),
                'ire': ecole.ville_ecole,
                'bp': ecole.bp_ecole,
                'contact': f"{ecole.telephone1}/{ecole.telephone2}",
                'email_ecole': ecole.email_ecole,
                'texte_brut': f"Les réinscriptions ouvrent aujourd'hui, {ecole.delai_reinscription.strftime('%d/%m/%Y')}.",
                'nom_ecole': ecole.nom_ecole,
            }
            if eleve.email_pere:
                destinataires.append((eleve.email_pere, contexte))
            if eleve.email_mere and eleve.email_mere != eleve.email_pere:
                destinataires.append((eleve.email_mere, contexte))

            contexte_sms = {                                                    
                'nom_eleve': f"{eleve.prenom} {eleve.nom}",                      
                'nom_ecole': ecole.nom_ecole,                                    
                'date_ouverture': ecole.delai_reinscription.strftime('%d/%m/%Y'),
            }           
            if eleve.contact_pere:                                          
                destinataires_sms.append((eleve.contact_pere, contexte_sms)) 
            if eleve.contact_mere and eleve.contact_mere != eleve.contact_pere: 
                destinataires_sms.append((eleve.contact_mere, contexte_sms))

            # détection des élèves sans aucun contact valide
            a_un_email = bool(eleve.email_pere or eleve.email_mere)
            a_un_telephone = bool(eleve.contact_pere or eleve.contact_mere)

            if not a_un_email and not a_un_telephone:
                eleves_sans_contact.append(f"{eleve.prenom} {eleve.nom}-{eleve.contact_mere}")


        envoyes, echecs = envoyer_emails_masse(
            destinataires,
            'emails/annonce_reinscription.html',
            sujet="Ouverture des réinscriptions"
        )

        self.stdout.write(self.style.SUCCESS(f"{envoyes} email(s) envoyé(s), {echecs} échec(s)."))

        # --- VÉRIFICATION DU SOLDE SMS ---
        sms_ok = True
        nb_sms_prevus = len(destinataires_sms)
        response = _client.accounts.get()
        if response.ok and response.data['balance'] < nb_sms_prevus:
            self.stdout.write(self.style.WARNING(
                f"Solde SMS insuffisant : {response.data['balance']} restant(s), {nb_sms_prevus} nécessaire(s)."
            ))
            sms_ok = False

        # --- FIN VÉRIFICATION ---
        if sms_ok:
            template_sms = (                                                        
            "Ecole {nom_ecole} : les reinscriptions pour {nom_eleve} ouvrent "  
            "le {date_ouverture}. Merci de vous rapprocher du service scolarite."  
                )                                                                       
            envoyes_sms, echecs_sms = envoyer_sms_masse(destinataires_sms, template_sms)  

            self.stdout.write(self.style.SUCCESS(f"{envoyes_sms} SMS envoyé(s), {echecs_sms} échec(s)."))

        # notification envoyée au gestionnaire comptable---
        if ecole.email_ecole:
            contexte_notif = {
                'titre': "Réinscriptions — Rapport d'envoi",
                'resume_texte': f"L'annonce d'ouverture des réinscriptions ({ecole.delai_reinscription.strftime('%d/%m/%Y')}) a été traitée.",
                'nb_concernes': eleves.count(),
                'envoyes_email': envoyes,
                'echecs_email': echecs,
                'envoyes_sms': envoyes_sms,
                'echecs_sms': echecs_sms,
                'eleves_sans_contact': eleves_sans_contact,
                'ire': ecole.ville_ecole,
                'bp': ecole.bp_ecole,
                'contact': f"{ecole.telephone1}/{ecole.telephone2}",
                'email_ecole': ecole.email_ecole,
                'nom_ecole': ecole.nom_ecole,
            }
            envoyes_notif, echecs_notif = envoyer_emails_masse(
                [(ecole.email_ecole, contexte_notif)],
                'emails/notification_gestionnaire.html',
                sujet="Rapport — Ouverture des réinscriptions"
            )
            self.stdout.write(f"Notification gestionnaire : {envoyes_notif} envoyé(s), {echecs_notif} échec(s).")
        else:
            self.stdout.write(self.style.WARNING("Aucun email configuré pour l'école — notification gestionnaire non envoyée."))     

