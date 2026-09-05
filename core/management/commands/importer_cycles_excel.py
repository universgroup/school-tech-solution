"""
Usage :
    python manage.py import_cycles /chemin/vers/Cycle.xlsx --dry-run
    python manage.py import_cycles /chemin/vers/Cycle.xlsx

Fichier attendu : colonnes ID, "Cycle scolaire" (ex: 1, "Maternelle")

Place ce fichier dans <app_name>/management/commands/import_cycles.py
TODO: remplacer <app_name> par le nom réel de l'app contenant CycleScolaire.

IMPORTANT : l'ID du fichier est réutilisé comme clé primaire en base, afin
que Classe.xlsx (colonne IDCycle) puisse continuer à référencer les mêmes
identifiants.

ATTENTION : le champ CycleScolaire.cycle a des choices (CYCLE_CHOICES).
Les valeurs du fichier ("Maternelle", "Primaire", "Collège", "Lycée SM",
"Lycée SS", "Lycée SE") doivent correspondre EXACTEMENT aux valeurs
autorisées par CYCLE_CHOICES dans vos models — vérifiez avant de lancer
l'import réel (le --dry-run n'effectue pas cette validation).

CIBLER UNE BASE PRECISE : par défaut Django écrit sur l'alias 'default' de
settings.DATABASES. Précisez l'alias exact si besoin :
    python manage.py import_cycles fichier.xlsx --database=production
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import openpyxl

from gAdministration.models import CycleScolaire 


class Command(BaseCommand):
    help = "Importe Cycle.xlsx vers le modèle CycleScolaire."

    def add_arguments(self, parser):
        parser.add_argument("fichier", type=str)
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument(
            "--database",
            type=str,
            default="default",
            help="Alias de base cible tel que défini dans settings.DATABASES (défaut: 'default').",
        )

    def handle(self, *args, **options):
        db_alias = options["database"]

        wb = openpyxl.load_workbook(options["fichier"], data_only=True)
        ws = wb.active

        headers = [str(c.value).strip() if c.value else "" for c in ws[1]]
        col = {name: idx for idx, name in enumerate(headers)}
        for required in ("ID", "Cycle scolaire"):
            if required not in col:
                raise CommandError(f"Colonne manquante: {required}")

        created, updated = 0, 0
        with transaction.atomic(using=db_alias):
            for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                legacy_id = row[col["ID"]]
                cycle = str(row[col["Cycle scolaire"]]).strip()
                if legacy_id is None or not cycle:
                    self.stdout.write(self.style.WARNING(f"Ligne {row_num} ignorée (incomplète)"))
                    continue

                if options["dry_run"]:
                    self.stdout.write(f"[DRY-RUN] id={legacy_id} cycle={cycle!r}")
                    continue

                obj, was_created = CycleScolaire.objects.using(db_alias).update_or_create(
                    id=legacy_id, defaults={"cycle": cycle}
                )
                created += int(was_created)
                updated += int(not was_created)

            if options["dry_run"]:
                transaction.set_rollback(True, using=db_alias)

        self.stdout.write(self.style.SUCCESS(
            f"[{db_alias}] Créés: {created} | Mis à jour: {updated}"
        ))