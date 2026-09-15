"""
Usage :
    python manage.py resync_sequences
    python manage.py resync_sequences --database=production
    python manage.py resync_sequences --only AnneeScolaire Classe

Resynchronise les séquences PostgreSQL des tables dont les ID ont été
insérés explicitement lors des imports legacy (AnneeScolaire, CycleScolaire,
Classe, Ecole, Eleve, Inscription, EtatPaiementTranche, ...).

A lancer après chaque import massif, ou ponctuellement si l'erreur
"duplicate key value violates unique constraint ..._pkey" réapparaît.

Place ce fichier dans <app_name>/management/commands/resync_sequences.py
TODO: remplacer <app_name> par le nom réel de l'app choisie pour héberger
cette commande utilitaire.
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
        "Resynchronise les séquences PostgreSQL (nextval) sur MAX(id) pour "
        "les tables importées avec des ID explicites (legacy)."
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
            self._resync_sequence(db_alias, model)

    def _resync_sequence(self, db_alias, model):
        table_name = model._meta.db_table
        pk_column = model._meta.pk.column  # gère le cas où la PK ne s'appelle pas "id"

        with connections[db_alias].cursor() as cursor:
            cursor.execute(
                "SELECT pg_get_serial_sequence(%s, %s)",
                [table_name, pk_column],
            )
            sequence_name = cursor.fetchone()[0]

            if sequence_name is None:
                self.stdout.write(self.style.WARNING(
                    f"[{model.__name__}] Aucune séquence trouvée pour {table_name}.{pk_column} "
                    "(PK non-serial ? déjà migré vers identity manuelle ?)"
                ))
                return

            cursor.execute(
                f'SELECT setval(%s, COALESCE((SELECT MAX("{pk_column}") FROM "{table_name}"), 1))',
                [sequence_name],
            )
            nouvelle_valeur = cursor.fetchone()[0]

        self.stdout.write(self.style.SUCCESS(
            f"[{db_alias}] {model.__name__} ({table_name}) → séquence resynchronisée à {nouvelle_valeur}"
        ))