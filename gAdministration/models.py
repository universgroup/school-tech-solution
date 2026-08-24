from django.db import models

CYCLE_CHOICES = [
    ('Selectionnez', 'Sélectionnez'),
    ('Maternelle', 'Maternelle'),
    ('Primaire', 'Primaire'),
    ('Collège', 'Collège'),
    ('Lycée SM', 'Lycée SM'),
    ('Lycée SS', 'Lycée SS'),
    ('Lycée SE', 'Lycée SE')
]


# Create your models here.
class AnneeScolaire(models.Model):
    descript_annee = models.CharField(max_length=10)

    def __str__(self):
        return self.descript_annee


class CycleScolaire(models.Model):
    cycle = models.CharField(max_length=15, default='Selectionnez', choices=CYCLE_CHOICES)

    def __str__(self):
        return self.cycle


class Classe(models.Model):
    nom_classe = models.CharField(max_length=20)
    frais_inscription = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frais_reinscription = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frais_scolarite = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    tranche1 = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tranche2 = models.DecimalField(max_digits=15, decimal_places=2, null=True, default=0)
    tranche3 = models.DecimalField(max_digits=15, decimal_places=2, null=True, default=0)
    idcycle = models.ForeignKey(CycleScolaire, on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.nom_classe)

    @property
    def cycle(self):
        return self.idcycle


class Ecole(models.Model):
    nom_ecole = models.CharField(max_length=50)
    ville_ecole = models.CharField(max_length=20)
    agrement_ecole = models.CharField(max_length=15)
    prefect_commune = models.CharField(max_length=15)
    bp_ecole = models.CharField(max_length=15, null=True)
    telephone1 = models.CharField(max_length=20)
    telephone2 = models.CharField(max_length=20, null=True)
    email_ecole = models.EmailField()
    site_internet = models.URLField(null=True)
    devise_ecole = models.CharField(max_length=50)
    logo_ecole = models.FileField(upload_to='media/', null=True, blank=True)
    dsee = models.CharField(max_length=30)
    dg = models.CharField(max_length=50)
    dga = models.CharField(max_length=50, null=True, blank=True)
    coordo_primaire = models.CharField(max_length=50, null=True)
    coordo_secondaire = models.CharField(max_length=50, null=True, blank=True)
    coordo_maternelle = models.CharField(max_length=50, null=True, blank=True)
    comptable = models.CharField(max_length=50, null=True)
    signa_dg = models.FileField(upload_to='media/', null=True, blank=True)
    signa_de = models.FileField(upload_to='media/', null=True, blank=True)
    delai_tranche1 = models.DateField(null=True) # Date limite fixée par la fondation pour le paiement de la première tranche de la scolarité
    delai_tranche2 = models.DateField(null=True) # Date limite fixée par la fondation pour le paiement de la seconde tranche de la scolarité
    delai_reinscription = models.DateField(null=True) # Date de début des reinscriptions fixée par la fondation


    def __str__(self):
        return '{} | {} | {} '.format(self.nom_ecole, self.ville_ecole, self.telephone1)


class Historique(models.Model):
    user_login = models.CharField(max_length=50)
    nature_operation = models.CharField(max_length=30)
    detail_operation = models.TextField()
    date_operation = models.DateField(auto_now=True)
    heure_op = models.TimeField(auto_now=True)
    email_user = models.EmailField(null=True)
    poste_travail = models.CharField(max_length=50, null=True) # C'est le nom du poste à partir duquel il s'est connecté

    def __str__(self):
        return '{} | {} | {} | {} | {} '.format(self.user_login, self.detail_operation, self.date_operation, self.email_user, self.poste_travail)
