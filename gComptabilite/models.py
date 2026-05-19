from django.db import models
from gAdministration.models import AnneeScolaire, Classe, Historique
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
    ('Fournitures Scolaires', 'Fournitures scolaires et de Bureau'),  # 4
    ('Autres Fournitures', 'Autres fournitures'),  # 5
    ('Investissements', 'Investissements'),  # 6
    ('Amortissements', 'Amortissements'),  # 7
    ('Charges Recurrentes', 'Charges récurrentes'),  # 8
    ('Créances', 'Créances'),  # 9
    ('Dettes', 'Dettes'),  # 10
    ('Autres Charges', 'Autres charges')  # 11
)

CATEGORIE_RECETTE_CHOICES = (
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('Scolarité', 'Scolarité'),  # 1
    ('Cours Revision', 'Cours révision'),  # 2
    ('Cours Coraniques', 'Cours coraniques'),  # 3
    ('Arriere Scolaire', 'Arriere scolaire'),  # 4
    ('Remboursement Prêt', 'Remboursement prêt'),  # 5
    ('Autres Recettes', 'Autres recettes')  # 6
)

TYPE_PAIEMENT_MENSUALITE_CHOICES = (
    ('Selectionnez', 'Sélectionnez'),
    ('Scolarite', 'Scolarité'),
    ('Cours Revision', 'Cours révision'),
    ('Cours Coraniques', 'Cours coraniques'),
    ('Arriere Scolaire', 'Arriere scolaire')
)

MOIS_CHOICES = (
    ('Selectionnez', 'Sélectionnez'),
    ('janvier', 'janvier'),
    ('fevrier', 'fevrier'),
    ('mars', 'mars'),
    ('avril', 'avril'),
    ('mai', 'mai'),
    ('juin', 'juin'),
    ('juillet', 'juillet'),
    ('aout', 'aout'),
    ('septembre', 'septembre'),
    ('octobre', 'octobre'),
    ('novembre', 'novembre'),
    ('decembre', 'decembre')
)


# Create your models here.
class Caisse(models.Model):
    libelle_operation = models.TextField()
    montant_encaisse = models.DecimalField(max_digits=20, decimal_places=2)
    type_operation = models.CharField(max_length=15, default=TYPE_OPERATION_CAISSE_CHOICES[0][0], choices=TYPE_OPERATION_CAISSE_CHOICES)
    date_operation = models.DateField(auto_now=True)
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
        return '{} {} {} '.format(self.libelle_operation, str(self.montant_encaisse), self.type_operation)

    @property
    def annee(self):
        return self.anscolaire


class EtatPaiementCoran(models.Model):
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    inscription = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    m_rabais = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjanvier = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    ffevreir = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fmars = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    favril = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fmai = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjuin = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjuillet = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    faout = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fseptembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fnovembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fdecembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.mateleve, self.inscription)

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.anneescolaire


class EtatPaiementRevision(models.Model):
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    inscription = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    m_rabais = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjanvier = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    ffevreir = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fmars = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    favril = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fmai = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjuin = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjuillet = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    faout = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fseptembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fnovembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fdecembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.mateleve, self.inscription)

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.anneescolaire


class EtatPaiementScolarite(models.Model):
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    inscription = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    m_rabais = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjanvier = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    ffevreir = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fmars = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    favril = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fmai = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjuin = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjuillet = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    faout = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fseptembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fnovembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fdecembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.mateleve, self.inscription)

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.anneescolaire


class PaiementCoran(models.Model):
    mois_paye = models.CharField(max_length=15, default='Selectionnez', choices=MOIS_CHOICES)
    date_payement = models.DateField(auto_now=True)
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    detail = models.TextField()
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mont_du = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reste_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {}'.format(self.mateleve, self.mois_paye, self.date_payement, str(self.montant_paye))

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.anneescolaire


class PaiementRevision(models.Model):
    mois_paye = models.CharField(max_length=15, default='Selectionnez', choices=MOIS_CHOICES)
    date_payement = models.DateField(auto_now=True)
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    detail = models.TextField()
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mont_du = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reste_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {} '.format(self.mateleve, self.mois_paye, self.date_payement, str(self.montant_paye))

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.anneescolaire


class PaiementScolarite(models.Model):
    mois_paye = models.CharField(max_length=15, default=MOIS_CHOICES[0][0], choices=MOIS_CHOICES)
    date_payement = models.DateField(auto_now=True)
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    detail = models.TextField()
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mont_du = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reste_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tranche_paye = models.CharField(max_length=25)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {}'.format(self.mateleve, self.mois_paye, self.date_payement, self.montant_paye)

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.anneescolaire
