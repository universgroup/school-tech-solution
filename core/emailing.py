from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from smtplib import SMTPException, SMTPServerDisconnected
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

    for email, contexte in destinataires_contexte:
        if not email:
            continue
        try:
            html_content = render_to_string(template_html, contexte)
            msg = EmailMultiAlternatives(
                subject=sujet,
                body=contexte.get('texte_brut', ''),
                to=[email],
                connection=connection,
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            envoyes += 1

        except (SMTPServerDisconnected, SMTPException) as e:
            # La connexion est morte (ex: quota Gmail dépassé) : on la referme
            # proprement, on en rouvre une neuve, et on retente Ce destinataire une fois.
            logger.warning(f"Connexion SMTP perdue avant envoi à {email} ({e}) — reconnexion...")
            try:
                connection.close()
            except Exception:
                pass
            connection = get_connection()
            connection.open()

            try:
                msg.connection = connection
                msg.send()
                envoyes += 1
            except Exception as e2:
                logger.error(f"Échec définitif envoi email à {email} : {e2}")
                echecs += 1

        except Exception as e:
            # Autres erreurs (template, adresse invalide, etc.) — pas liées à la connexion
            logger.error(f"Échec envoi email à {email} : {e}")
            echecs += 1

    try:
        connection.close()
    except Exception:
        pass

    return envoyes, echecs

