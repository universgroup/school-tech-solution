"""
Management command Django : import_eleves

Usage (depuis la racine du projet, en SSH sur cPanel) :
    python manage.py import_eleves /chemin/vers/Eleves.xlsx --dry-run
    python manage.py import_eleves /chemin/vers/Eleves.xlsx

Fichier attendu (version finale) : colonnes matricule, nom, prenom, sexe,
datenaissance, lieu_naissance, pays_naissance, pere, mere, adresse, tuteur,
ecole_origine, ID, date_arrivee, contact_mere, contact_pere, email_pere,
email_mere, profes_pere, profes_mere, personne_contact.

Champs du modèle Eleve non couverts par ce fichier (laissés vides / valeur
par défaut) : photo_eleve, date_depart, depart (reste à False).

IMPORTANT : les placeholders "X", "Xxxx", "xxxxxxxx", etc. présents dans le
fichier sont enregistrés TELS QUELS en base — ils ne sont ni nettoyés ni
convertis en valeur vide.

Pré-requis :
    pip install openpyxl --break-system-packages

À FAIRE AVANT DE LANCER :
    1. Placer ce fichier dans <votre_app>/management/commands/import_eleves.py
       (créer les dossiers management/ et management/commands/ avec un
       __init__.py vide dans chacun s'ils n'existent pas déjà).
    2. Remplacer <app_name> ci-dessous par le nom réel de l'app contenant
       le modèle Eleve.

CIBLER UNE BASE PRECISE : par défaut Django écrit sur l'alias 'default' de
settings.DATABASES. Précisez l'alias exact si besoin :
    python manage.py import_eleves fichier.xlsx --database=production
"""

import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import openpyxl

from gEleve.models import Eleve


def parse_date(value):
    """Accepte un objet date/datetime Excel natif, ou une chaîne jj/MM/aaaa ou aaaa-MM-jj."""
    if value in (None, ""):
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Format de date non reconnu: {value!r}")


def as_text(value):
    """Convertit en texte et retire les espaces superflus, sans altérer le contenu
    (les placeholders "X"/"Xxxx" etc. sont conservés tels quels)."""
    if value is None:
        return ""
    return str(value).strip()


class Command(BaseCommand):
    help = "Importe les élèves depuis Eleves.xlsx (version finale) vers le modèle Eleve."

    def add_arguments(self, parser):
        parser.add_argument("fichier", type=str, help="Chemin vers Eleves.xlsx")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="N'écrit rien en base, affiche seulement ce qui serait fait.",
        )
        parser.add_argument(
            "--database",
            type=str,
            default="default",
            help="Alias de base cible tel que défini dans settings.DATABASES (défaut: 'default').",
        )

    def handle(self, *args, **options):
        db_alias = options["database"]
        dry_run = options["dry_run"]

        wb = openpyxl.load_workbook(options["fichier"], data_only=True)
        ws = wb.active

        headers = [str(c.value).strip() if c.value else "" for c in ws[1]]
        col = {name: idx for idx, name in enumerate(headers)}

        required_cols = [
            "matricule", "nom", "prenom", "sexe", "datenaissance", "lieu_naissance",
            "pays_naissance", "pere", "mere", "adresse", "tuteur", "ecole_origine",
            "ID", "date_arrivee", "contact_mere", "contact_pere", "email_pere",
            "email_mere", "profes_pere", "profes_mere", "personne_contact",
        ]
        missing = [c for c in required_cols if c not in col]
        if missing:
            raise CommandError(f"Colonnes absentes du fichier: {missing}")

        created, updated, errors = 0, 0, []

        with transaction.atomic(using=db_alias):
            for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                def val(name):
                    return row[col[name]]

                matricule = as_text(val("matricule"))
                if not matricule:
                    errors.append((row_num, "matricule manquant — ligne ignorée"))
                    continue

                try:
                    datenaissance = parse_date(val("datenaissance"))
                    date_arrivee = parse_date(val("date_arrivee"))
                except ValueError as exc:
                    errors.append((row_num, str(exc)))
                    continue

                defaults = {
                    "ideleve": val("ID"),
                    "nom": as_text(val("nom")),
                    "prenom": as_text(val("prenom")),
                    "sexe_eleve": as_text(val("sexe")),
                    "pere": as_text(val("pere")),
                    "mere": as_text(val("mere")),
                    "tuteur": as_text(val("tuteur")),
                    "contact_pere": as_text(val("contact_pere")),
                    "contact_mere": as_text(val("contact_mere")) or None,
                    "email_pere": as_text(val("email_pere")),
                    "email_mere": as_text(val("email_mere")) or None,
                    "profes_pere": as_text(val("profes_pere")) or None,
                    "profes_mere": as_text(val("profes_mere")) or None,
                    "personne_contact": as_text(val("personne_contact")) or None,
                    "adresse": as_text(val("adresse")),
                    "ecole_origine": as_text(val("ecole_origine")),
                    "datenaissance": datenaissance,
                    "lieu_naissance": as_text(val("lieu_naissance")),
                    "pays_naissance": as_text(val("pays_naissance")),
                    "date_arrivee": date_arrivee,
                }

                if dry_run:
                    self.stdout.write(f"[DRY-RUN] {matricule}: {defaults}")
                    continue

                obj, was_created = Eleve.objects.using(db_alias).update_or_create(
                    matricule=matricule, defaults=defaults
                )
                created += int(was_created)
                updated += int(not was_created)

            if dry_run:
                transaction.set_rollback(True, using=db_alias)

        self.stdout.write(self.style.SUCCESS(f"[{db_alias}] Créés: {created} | Mis à jour: {updated}"))
        if errors:
            self.stdout.write(self.style.ERROR(f"{len(errors)} ligne(s) en erreur:"))
            for row_num, msg in errors:
                self.stdout.write(f"  ligne {row_num}: {msg}")