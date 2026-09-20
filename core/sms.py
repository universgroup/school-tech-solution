import re
import logging
from django.conf import settings
from nimbasms import Client

logger = logging.getLogger(__name__)

# Le client est instancié une seule fois au chargement du module, pas à chaque appel
_client = Client(settings.NIMBA_SMS_ACCOUNT_SID, settings.NIMBA_SMS_AUTH_TOKEN)


def normaliser_numero_gn(numero):
    """Convertit un numéro guinéen local en format attendu par NimbaSMS : 224XXXXXXXXX (sans '+')."""
    if not numero:
        return None
    chiffres = re.sub(r'\D', '', numero)  # retire espaces, tirets, '+', etc.
    if chiffres.startswith('224'):
        return chiffres
    if chiffres.startswith('0'):
        chiffres = chiffres[1:]
    if len(chiffres) == 9:
        return f"224{chiffres}"
    return None  # numéro invalide


def envoyer_sms_masse(destinataires_contexte, template_message, sender_name="EChampions"):
    """
    destinataires_contexte : liste de tuples (telephone, contexte_dict)
    template_message : chaîne de format Python avec {placeholders}
    sender_name : nom d'expéditeur, à valider au préalable dans votre espace NimbaSMS
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

        try:
            response = _client.messages.create(
                to=[numero],
                sender_name=sender_name,
                message=message,
            )
            if response.ok:
                envoyes += 1
            else:
                logger.error(f"Échec envoi SMS à {numero} : {response.data}")
                echecs += 1
        except Exception as e:
            logger.error(f"Erreur envoi SMS à {numero} : {e}")
            echecs += 1

    return envoyes, echecs