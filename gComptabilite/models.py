from django.db import models
from gAdministration.models import AnneeScolaire, Classe, CycleScolaire
from gEleve.models import Eleve

TYPE_OPERATION_CAISSE_CHOICES = (
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('Recette', 'Recette'),  # 1
    ('Dépense', 'Dépense')  # 2
)

CATEGORIE_DEPENSE_CHOICES = (
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('Salaires', 'Salaires'),  # 1
    ('Charges locatives', 'Charges locatives'),  # 2
    ('Mobiliers et Infrastructures', 'Mobiliers et Infrastructures'),  # 3
    ('Fournitures Scolaires', 'Fournitures Scolaires'),  # 4
    ('Fournitures Bureau','Fournitures de Bureau'), # 5
    ('Autres Fournitures', 'Autres Fournitures'),  # 6
    ('Investissements', 'Investissements'),  # 7
    ('Amortissements', 'Amortissements'),  # 8
    ('Charges Recurrentes', 'Charges Récurrentes'),  # 9
    ('Creances', 'Créances'),  # 10
    ('Dettes Fournisseurs', 'Dettes Fournisseurs'),  # 11
    ('Autres Charges', 'Autres Charges'),  # 12
    ('Materiels Informatiques','Matériels Informatiques'), # 13
    ('Materiels Didactiques','Matériels Didactiques'), # 14
    ('Banque','Banque'), # 15
    ('Primes stagiaires','Primes stagiaires'), # 16
    ('Facture Fournisseurs','Facture Fournisseurs'), # 17
    ('Facture Intervenant','Facture Intervenant'), # 18
    ('Facture Prestataire','Facture Prestataire'), # 19
    ('Impots','Impôts'), # 20
    ('CNSS','CNSS'), # 21
    ('Homme Charge','Homme de Charge'), # 22

)

CATEGORIE_RECETTE_CHOICES = (
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('Scolarité', 'Scolarité'),  # 1
    ('Cantine', 'Cantine'),  # 2
    ('Sport', 'Sport'),  # 3
    ('Karaté','Karaté'), # 4
    ('Natation','Natation'), # 5
    ('Autres Extra Scolaires','Autres Extra Scolaires'), # 6
    ('Arriere Scolaire', 'Arriere scolaire'),  # 7
    ('Remboursement Prêt', 'Remboursement prêt'),  # 8
    ('Autres Recettes', 'Autres recettes')  # 9
)

TYPE_PAIEMENT_MENSUALITE_CHOICES = (
    ('Selectionnez', 'Sélectionnez'), # 0
    ('Scolarite', 'Scolarité'), # 1
    ('Cours Revision', 'Cours révision'), # 2
    ('Cours Coraniques', 'Cours coraniques'), # 3
    ('Arriere Scolaire', 'Arriere scolaire') # 4
)

DEUX_TRANCHES_CHOICES = (
    ('PremiereT', 'Première tranche'), # 0
    ('DeuxiemeT', 'Deuxième tranche') # 1
)

TROIS_TRANCHES_CHOICES = (
    ('PremiereT', 'Première tranche'), # 0
    ('DeuxiemeT', 'Deuxième tranche'), # 1
    ('TroisiemeT','Troisième tranche') # 2
)

MODE_PAIEMENT_CHOICES = (
    ('Espèce','Espèce'), # 0
    ('Chèque','Chèque'), # 1
    ('Virement bancaire','Virement bancaire'), # 2
    ('Orange Money','Orange Money'), # 3
    ('MTN Mobile Money','MTN Mobile Money'), # 4
)


# Create your models here.
class Caisse(models.Model):
    libelle_operation = models.TextField()
    montant_encaisse = models.DecimalField(max_digits=20, decimal_places=2)
    type_operation = models.CharField(max_length=15, default=TYPE_OPERATION_CAISSE_CHOICES[1][0], choices=TYPE_OPERATION_CAISSE_CHOICES)
    date_operation = models.DateField(null=True) # Il se peut qu'en pratique l'opération soit effectuée avant la date du jour. Donc, l'utilisateur a besoin de saisir
    solde_actuel = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    heure_operation = models.TimeField(auto_now=True)
    qte = models.IntegerField(null=True, default=0)
    pua = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    provient = models.CharField(max_length=50, null=True)
    destine = models.CharField(max_length=50, null=True)
    observ = models.CharField(max_length=90, null=True)
    anscolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    piece_jointe = models.FileField(upload_to='media/', null=True, blank=True)
    categ_depense = models.CharField(max_length=100, default=CATEGORIE_DEPENSE_CHOICES[0][0])

    def __str__(self):
        return '{} | {} | {} | {}'.format(self.date_operation,self.libelle_operation, str(self.montant_encaisse), self.type_operation)

    @property
    def annee(self):
        return self.anscolaire


class EtatPaiementTranche(models.Model):
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    inscription = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    m_rabais = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    premiere_tranche = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    deuxieme_tranche = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    troisieme_tranche = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True) # Pour le cas des écoles qui font payer jusqu'à trois tranches
    fscolarite = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    reste_a_payer = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    date_paie = models.DateField()
    mode_paie = models.CharField(max_length=50, choices=MODE_PAIEMENT_CHOICES, default=MODE_PAIEMENT_CHOICES[0][0], null=True)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)
    idcycle = models.ForeignKey(CycleScolaire, on_delete=models.CASCADE)

    def __str__(self):
        return '{} | {} | {} | {}'.format(self.mateleve, self.inscription, self.premiere_tranche, self.deuxieme_tranche)

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.anneescolaire
    
    @property
    def cycle(self):
        return self.idcycle
