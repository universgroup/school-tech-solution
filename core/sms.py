# core/sms.py
import re
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

SMS_API_URL = "https://api.smspartner.fr/v1/send"

def normaliser_numero_gn(numero):
    """Convertit un numéro guinéen local en format international +224XXXXXXXX."""
    if not numero:
        return None
    chiffres = re.sub(r'\D', '', numero)  # retire espaces, tirets, etc.
    if chiffres.startswith('224'):
        return f"+{chiffres}"
    if chiffres.startswith('0'):
        chiffres = chiffres[1:]
    if len(chiffres) == 9:
        return f"+224{chiffres}"
    return None  # numéro invalide, à logger


def envoyer_sms_masse(destinataires_contexte, template_message, sender="E Champions"):
    """
    destinataires_contexte : liste de tuples (telephone, contexte_dict)
    template_message : chaîne de format Python avec {placeholders}, ex:
        "Bonjour, la reinscription pour {nom_eleve} ouvre le {date_ouverture}."
    sender : nom d'expéditeur (max 11 caractères alphanumériques, à valider au préalable
             auprès du fournisseur — certains opérateurs GN imposent une validation manuelle)
    """
    envoyes, echecs = 0, 0

    for telephone, contexte in destinataires_contexte:
        numero = normaliser_numero_gn(telephone)
        if not numero:
            logger.warning(f"Numéro invalide ignoré : {telephone}")
            echecs += 1
            continue

        try:
            message = template_message.format(**contexte)
        except KeyError as e:
            logger.error(f"Variable manquante dans le template SMS : {e}")
            echecs += 1
            continue

        payload = {
            "apiKey": settings.SMS_API_KEY,
            "phoneNumbers": numero,
            "sender": sender,
            "gamme": 1,
            "message": message,
        }

        try:
            resp = requests.post(SMS_API_URL, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if data.get("success", True):
                envoyes += 1
            else:
                logger.error(f"Échec envoi SMS à {numero} : {data}")
                echecs += 1
        except requests.RequestException as e:
            logger.error(f"Erreur réseau envoi SMS à {numero} : {e}")
            echecs += 1

    return envoyes, echecs