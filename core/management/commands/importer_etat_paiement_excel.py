"""
Usage :
    python manage.py import_etats_paiement /chemin/vers/EtatPaiement.xlsx --dry-run
    python manage.py import_etats_paiement /chemin/vers/EtatPaiement.xlsx

Fichier attendu (version épurée, PAR HYPOTHESE — à confirmer avec les
vrais en-têtes une fois le fichier exporté) : colonnes IDEtat, IDannee,
IDCycle, IDclasse, Matricule, inscription, premiere_tranche,
deuxieme_tranche, troixième_tranche, fscolarite, mtremise, reste_apaye,
date_paie.

IDannee, IDCycle et IDclasse sont supposés être, comme pour
Inscription.xlsx, de vrais identifiants numériques legacy correspondant
directement aux clés primaires préservées par import_annee_scolaire,
import_cycles et import_classes. Si les en-têtes réels diffèrent une fois
le fichier exporté, ajustez simplement la liste required_cols et les
appels val(...) ci-dessous — le reste de la logique ne change pas.

Place ce fichier dans <app_name>.models EtatPaiementTranche — app gComptabilite.
TODO: remplacer <app_name> par le nom réel de l'app (gComptabilite) et
<app_eleve> par le nom de l'app contenant Eleve/Classe/AnneeScolaire/CycleScolaire
si elle diffère.

PRE-REQUIS : import_annee_scolaire, import_cycles, import_classes et
l'import des Eleve doivent avoir été exécutés avant (avec les mêmes id
legacy).

--- mode_paie ---------------------------------------------------------
Absent du fichier. Le champ a un default dans le modèle
(MODE_PAIEMENT_CHOICES[0][0]) : il est donc simplement omis des `defaults`
ci-dessous, Django appliquera le default du modèle à la création. Si vous
voulez un mode explicite pour tous ces enregistrements legacy, ajoutez-le
manuellement dans DEFAULT_MODE_PAIE plus bas.

CIBLER UNE BASE PRECISE : par défaut Django écrit sur l'alias 'default' de
settings.DATABASES. Précisez l'alias exact si besoin :
    python manage.py import_etats_paiement fichier.xlsx --database=production
"""

import datetime
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import openpyxl

from gComptabilite.models import EtatPaiementTranche 
from gAdministration.models import AnneeScolaire, Classe, CycleScolaire 
from gEleve.models import Eleve


# Optionnel : décommentez et fixez une valeur si vous voulez un mode_paie
# explicite plutôt que le default du modèle pour tous ces enregistrements.
DEFAULT_MODE_PAIE = None


def to_decimal(value):
    if value in (None, ""):
        return Decimal("0")
    try:
        return Decimal(str(value))
    except InvalidOperation:
        raise ValueError(f"Montant invalide: {value!r}")


def parse_date(value):
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


class Command(BaseCommand):
    help = "Importe EtatPaiement.xlsx (version épurée) vers le modèle EtatPaiementTranche."

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
        dry_run = options["dry_run"]

        wb = openpyxl.load_workbook(options["fichier"], data_only=True)
        ws = wb.active

        headers = [str(c.value).strip() if c.value else "" for c in ws[1]]
        col = {name: idx for idx, name in enumerate(headers)}
        required_cols = [
            "IDEtat", "IDannee", "IDCycle", "IDclasse", "Matricule",
            "inscription", "premiere_tranche", "deuxieme_tranche",
            "troixième_tranche", "fscolarite", "mtremise", "reste_apaye",
            "date_paie",
        ]
        missing = [c for c in required_cols if c not in col]
        if missing:
            raise CommandError(f"Colonnes manquantes: {missing}")

        created, updated, errors = 0, 0, []

        with transaction.atomic(using=db_alias):
            for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                def val(name):
                    return row[col[name]]

                legacy_id = val("IDEtat")
                matricule = str(val("Matricule") or "").strip()
                idannee = val("IDannee")
                idcycle = val("IDCycle")
                idclasse = val("IDclasse")

                if not all([legacy_id, matricule, idannee, idcycle, idclasse]):
                    errors.append((row_num, "ligne incomplète — ignorée"))
                    continue

                try:
                    eleve = Eleve.objects.using(db_alias).get(matricule=matricule)
                except Eleve.DoesNotExist:
                    errors.append((row_num, f"Eleve matricule={matricule!r} introuvable"))
                    continue

                try:
                    classe = Classe.objects.using(db_alias).get(id=idclasse)
                except Classe.DoesNotExist:
                    errors.append((row_num, f"Classe id={idclasse!r} introuvable — lancez import_classes d'abord"))
                    continue

                try:
                    cycle = CycleScolaire.objects.using(db_alias).get(id=idcycle)
                except CycleScolaire.DoesNotExist:
                    errors.append((row_num, f"CycleScolaire id={idcycle!r} introuvable — lancez import_cycles d'abord"))
                    continue

                try:
                    annee = AnneeScolaire.objects.using(db_alias).get(id=idannee)
                except AnneeScolaire.DoesNotExist:
                    errors.append((row_num, f"AnneeScolaire id={idannee!r} introuvable — lancez import_annee_scolaire d'abord"))
                    continue

                try:
                    date_paie = parse_date(val("date_paie"))
                    defaults = {
                        "anneescolaire": annee,
                        "mateleve": eleve,
                        "idclasse": classe,
                        "idcycle": cycle,
                        "inscription": to_decimal(val("inscription")),
                        "m_rabais": to_decimal(val("mtremise")),
                        "premiere_tranche": to_decimal(val("premiere_tranche")),
                        "deuxieme_tranche": to_decimal(val("deuxieme_tranche")),
                        "troisieme_tranche": to_decimal(val("troixième_tranche")),
                        "fscolarite": to_decimal(val("fscolarite")),
                        "reste_a_payer": to_decimal(val("reste_apaye")),
                        "date_paie": date_paie,
                    }
                except ValueError as exc:
                    errors.append((row_num, str(exc)))
                    continue

                if date_paie is None:
                    errors.append((row_num, "date_paie manquante (champ non-nullable) — ligne ignorée"))
                    continue

                if DEFAULT_MODE_PAIE is not None:
                    defaults["mode_paie"] = DEFAULT_MODE_PAIE

                if dry_run:
                    self.stdout.write(
                        f"[DRY-RUN] id={legacy_id} matricule={matricule} classe_id={idclasse} "
                        f"cycle_id={idcycle} annee_id={idannee} {defaults}"
                    )
                    continue

                obj, was_created = EtatPaiementTranche.objects.using(db_alias).update_or_create(
                    id=legacy_id, defaults=defaults
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