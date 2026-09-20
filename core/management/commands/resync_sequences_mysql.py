"""
Usage :
    python manage.py resync_autoincrement
    python manage.py resync_autoincrement --database=production
    python manage.py resync_autoincrement --only AnneeScolaire Classe

Equivalent MySQL de resync_sequences.py (PostgreSQL). MySQL ne connaît pas
les séquences : chaque table auto-incrémentée porte directement sa valeur
courante dans AUTO_INCREMENT (visible via `SHOW TABLE STATUS` ou
information_schema.TABLES). Cette commande recale AUTO_INCREMENT sur
MAX(id) + 1 pour les tables dont les ID ont été insérés explicitement lors
des imports legacy.

A lancer après chaque import massif, ou ponctuellement si l'erreur
"Duplicate entry '...' for key '...PRIMARY'" apparaît lors d'une création
normale via l'application (signe qu'AUTO_INCREMENT est resté à une valeur
inférieure aux ID déjà présents).

Place ce fichier dans <app_name>/management/commands/resync_autoincrement.py
TODO: remplacer <app_name> par le nom réel de l'app choisie pour héberger
cette commande utilitaire.

NOTE CASSE : contrairement à PostgreSQL, MySQL sous Linux est
sensible à la casse des noms de table par défaut (lower_case_table_names=0),
donc gAdministration_anneescolaire (avec le A majuscule) doit rester tel
quel. connection.ops.quote_name() gère ça correctement pour ce backend
(guillemets ` ` au lieu de " " utilisés par PostgreSQL) — même logique de
prudence que pour la version PostgreSQL, appliquée ici par précaution même
si MySQL ne replie pas la casse comme le fait pg_get_serial_sequence.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connections

from gAdministration.models import AnneeScolaire, CycleScolaire, Classe, Ecole
from gEleve.models import Eleve, Inscription
from gComptabilite.models import EtatPaiementTranche


# Liste centrale des modèles concernés par les imports avec ID explicites.
# Ajoute ou retire des entrées ici au fur et à mesure de tes imports.
MODELES_A_RESYNC = [
    AnneeScolaire,
    CycleScolaire,
    Classe,
    Ecole,
    Eleve,
    Inscription,
    EtatPaiementTranche,
]


class Command(BaseCommand):
    help = (
        "Recale AUTO_INCREMENT sur MAX(id) + 1 (MySQL) pour les tables "
        "importées avec des ID explicites (legacy)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            type=str,
            default="default",
            help="Alias de base cible tel que défini dans settings.DATABASES (défaut: 'default').",
        )
        parser.add_argument(
            "--only",
            nargs="+",
            help="Limiter la resynchronisation à ces noms de modèles (ex: --only AnneeScolaire Classe).",
        )

    def handle(self, *args, **options):
        db_alias = options["database"]
        only = set(options["only"]) if options["only"] else None

        if db_alias not in connections:
            raise CommandError(f"Alias de base inconnu: {db_alias}")

        vendor = connections[db_alias].vendor
        if vendor != "mysql":
            raise CommandError(
                f"L'alias '{db_alias}' pointe vers un backend '{vendor}', pas MySQL. "
                "Utilisez resync_sequences (PostgreSQL) pour cette base."
            )

        modeles = MODELES_A_RESYNC
        if only:
            modeles = [m for m in modeles if m.__name__ in only]
            noms_trouves = {m.__name__ for m in modeles}
            manquants = only - noms_trouves
            if manquants:
                self.stdout.write(self.style.WARNING(
                    f"Modèles inconnus ignorés: {', '.join(manquants)}"
                ))

        if not modeles:
            self.stdout.write(self.style.WARNING("Aucun modèle à traiter."))
            return

        for model in modeles:
            self._resync_auto_increment(db_alias, model)

    def _resync_auto_increment(self, db_alias, model):
        table_name = model._meta.db_table
        pk_column = model._meta.pk.column  # gère le cas où la PK ne s'appelle pas "id"
        quote_name = connections[db_alias].ops.quote_name

        table_quoted = quote_name(table_name)
        column_quoted = quote_name(pk_column)

        with connections[db_alias].cursor() as cursor:
            cursor.execute(f"SELECT MAX({column_quoted}) FROM {table_quoted}")
            max_id = cursor.fetchone()[0]

            if max_id is None:
                self.stdout.write(self.style.WARNING(
                    f"[{model.__name__}] Table {table_name} vide — AUTO_INCREMENT non modifié."
                ))
                return

            nouvelle_valeur = int(max_id) + 1

            # DDL : MySQL n'accepte pas de paramètre lié (%s) sur ALTER TABLE,
            # d'où la validation explicite en int ci-dessus avant d'insérer
            # la valeur directement dans la requête (évite toute injection).
            cursor.execute(
                f"ALTER TABLE {table_quoted} AUTO_INCREMENT = {nouvelle_valeur}"
            )

        self.stdout.write(self.style.SUCCESS(
            f"[{db_alias}] {model.__name__} ({table_name}) → AUTO_INCREMENT recalé à {nouvelle_valeur}"
        ))