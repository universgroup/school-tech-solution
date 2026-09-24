from django.core.management.base import BaseCommand
from datetime import datetime, timedelta # timedelta est une classe qui permet de calculer la durée entre deux dates
from core.emailing import envoyer_emails_masse
from core.sms import envoyer_sms_masse, _client

from gAdministration.models import Ecole
from gComptabilite.models import EtatPaiementTranche

class Command(BaseCommand):
    help = "Envoie un rappel par email aux parents dont la date limite de paiement (tranche 1 ou 2) approche (7 jours)"

    def handle(self, *args, **options):
        aujourdhui = datetime.now().date()
        date_seuil = aujourdhui + timedelta(days=7)
        self.stdout.write(f"[Rappels paiement] Vérification au {aujourdhui} (seuil = {date_seuil})")

        ecole = Ecole.objects.first()
        if not ecole:
            self.stdout.write(self.style.ERROR("Aucune information d'école configurée."))
            return

        # --- Tranche 1 ---
        if ecole.delai_tranche1 == date_seuil:
            self.envoyer_rappel_tranche(ecole,champ_paye='premiere_tranche', champ_montant='tranche1', nom_tranche_libelle="1ère tranche", date_limite=ecole.delai_tranche1)
        else:
            self.stdout.write(f"Tranche 1 : pas de rappel aujourd'hui (délai configuré : {ecole.delai_tranche1}).")

        # --- Tranche 2 ---
        if ecole.delai_tranche2 == date_seuil:
            self.envoyer_rappel_tranche(ecole,champ_paye='deuxieme_tranche', champ_montant='tranche2', nom_tranche_libelle="2ème tranche", date_limite=ecole.delai_tranche2)
        else:
            self.stdout.write(f"Tranche 2 : pas de rappel aujourd'hui (délai configuré : {ecole.delai_tranche2}).")


    def envoyer_rappel_tranche(self, ecole, champ_paye, champ_montant, nom_tranche_libelle, date_limite):
    # Toutes les données nécessaires en une seule requête (mateleve + idclasse pour le montant de la tranche)
        etatpaie = EtatPaiementTranche.objects.select_related('mateleve', 'idclasse')
       
        destinataires = []
        destinataires_sms = []
        eleves_sans_contact = []
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
                'ire': ecole.ville_ecole,
                'bp': ecole.bp_ecole,
                'contact': f"{ecole.telephone1}/{ecole.telephone2}",
                'email_ecole': ecole.email_ecole,
                'nom_ecole': ecole.nom_ecole,
                'texte_brut': f"Rappel : la date limite de paiement de la {nom_tranche_libelle} est le {date_limite.strftime('%d/%m/%Y')}.",
            }
            if eleve.email_pere:
                destinataires.append((eleve.email_pere, contexte))
            if eleve.email_mere and eleve.email_mere != eleve.email_pere:
                destinataires.append((eleve.email_mere, contexte))

            contexte_sms = {                                                    
                'nom_eleve': f"{eleve.prenom} {eleve.nom}",                      
                'nom_tranche': nom_tranche_libelle,                              
                'reste_a_payer': '{:,}'.format(reste_tranche),                   
                'date_limite': date_limite.strftime('%d/%m/%Y'), 
                'nom_ecole': ecole.nom_ecole,                
            }                                                                    
            if eleve.contact_pere:                                            
                destinataires_sms.append((eleve.contact_pere, contexte_sms))  
            if eleve.contact_mere and eleve.contact_mere != eleve.contact_pere:  
                destinataires_sms.append((eleve.contact_mere, contexte_sms))

            # dans la boucle, après avoir déterminé reste_tranche > 0
            a_un_email = bool(eleve.email_pere or eleve.email_mere)
            a_un_telephone = bool(eleve.contact_pere or eleve.contact_mere)

            if not a_un_email and not a_un_telephone:
                eleves_sans_contact.append(f"{eleve.prenom} {eleve.nom}-{eleve.contact_mere}- ({classe})")

        self.stdout.write(f"{nb_concernes} élève(s) concerné(s) par le rappel {nom_tranche_libelle}.")

        envoyes, echecs = envoyer_emails_masse(
            destinataires,
            'emails/rappel_paiement.html',
            sujet=f"Rappel : date limite de paiement — {nom_tranche_libelle}"
        )

        self.stdout.write(self.style.SUCCESS(f"{envoyes} email(s) envoyé(s), {echecs} échec(s) pour la {nom_tranche_libelle}."))

        # --- VÉRIFICATION DU SOLDE SMS---

        sms_ok = True
        nb_sms_prevus = len(destinataires_sms)
        response = _client.accounts.get()
        if response.ok and response.data['balance'] < nb_sms_prevus:
            self.stdout.write(self.style.WARNING(
                f"Solde SMS insuffisant pour {nom_tranche_libelle} : {response.data['balance']} restant(s), {nb_sms_prevus} nécessaire(s)."
            ))
            sms_ok = False
            envoyes_sms, echecs_sms = 0, nb_sms_prevus
           
        # --- FIN VÉRIFICATION ---
        if sms_ok:
            template_sms = (                                                         
            "Ecole {nom_ecole} : rappel, la {nom_tranche} de {nom_eleve} "       
            "doit être réglée avant le {date_limite}. Reste : {reste_a_payer} GNF."  
            )                                 
            envoyes_sms, echecs_sms = envoyer_sms_masse(destinataires_sms, template_sms)

            self.stdout.write(self.style.SUCCESS(f"{envoyes_sms} SMS envoyé(s), {echecs_sms} échec(s) pour la {nom_tranche_libelle}."))

        # notification au gestionnaire ---
        if ecole.email_ecole:
            contexte_notif = {
                'titre': f"Rappel {nom_tranche_libelle} — Rapport d'envoi",
                'resume_texte': f"Le rappel de paiement pour la {nom_tranche_libelle} (échéance {date_limite.strftime('%d/%m/%Y')}) a été traité.",
                'nb_concernes': nb_concernes,
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
                sujet=f"Rapport — Rappel {nom_tranche_libelle}"
            )
            self.stdout.write(f"Notification gestionnaire : {envoyes_notif} envoyé(s), {echecs_notif} échec(s).")
        else:
            self.stdout.write(self.style.WARNING("Aucun email configuré pour l'école — notification gestionnaire non envoyée."))    

                                            