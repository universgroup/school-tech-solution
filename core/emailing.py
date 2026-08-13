from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


def envoyer_emails_masse(destinataires_contexte, template_html, sujet):
    """
    destinataires_contexte : liste de tuples (email, contexte_dict)
    template_html : chemin du template email (avec balises Django classiques)
    """
    connection = get_connection()
    connection.open()

    envoyes, echecs = 0, 0
    try:
        for email, contexte in destinataires_contexte:
            if not email:
                continue
            try:
                html_content = render_to_string(template_html, contexte)
                msg = EmailMultiAlternatives(
                    subject=sujet,
                    body=contexte.get('texte_brut', ''),   # version texte simple, fallback
                    to=[email],
                    connection=connection,
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                envoyes += 1
            except Exception as e:
                logger.error(f"Échec envoi email à {email} : {e}")
                echecs += 1
    finally:
        connection.close()

    return envoyes, echecs