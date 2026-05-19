from django.db import models
from gAdministration.models import AnneeScolaire
from gComptabilite.models import MOIS_CHOICES

CIVILITE_CHOICES = [
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('Monsieur', 'Monsieur'),  # 1
    ('Madame', 'Madame'),  # 2
    ('Madémoiselle', 'Madémoisselle')  # 3
]

TYPE_PERSONNEL = (
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('Vacataire', 'Vacataire'),  # 1
    ('Permanent', 'Permanent')  # 2
)

SEXE_PERSONNEL = (
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('Homme', 'Homme'),  # 1
    ('Femme', 'Femme')  # 2
)

CONTRAT_CHOICES = (
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('CDD', 'CDD'),  # 1
    ('CDI', 'CDI')  # 2
)

# Create your models here.
class Personnel(models.Model):
    nom_personnel = models.CharField(max_length=30)
    prenom_personnel = models.CharField(max_length=50)
    civilite = models.CharField(max_length=15, default='Selectionnez', choices=CIVILITE_CHOICES)
    date_naissance = models.DateField()
    niveau_etude = models.CharField(max_length=50)
    type_personnel = models.CharField(max_length=15, default='Selectionnez', choices=TYPE_PERSONNEL)
    adresse_personnel = models.CharField(max_length=50)
    contact_personnel = models.CharField(max_length=25)
    fonction_personnel = models.CharField(max_length=35)
    email_personnel = models.EmailField()
    sexe_personnel = models.CharField(max_length=15, default='Selectionnez', choices=SEXE_PERSONNEL)
    salbase = models.DecimalField(max_digits=10, decimal_places=2)
    annee_experience = models.CharField(max_length=10)
    contrat_type = models.CharField(max_length=15, default='Selectionnez', choices=CONTRAT_CHOICES)
    diplome = models.CharField(max_length=25)
    date_embauche = models.DateField()

    def __str__(self):
        return '{} | {} | {} | {}'.format(self.nom_personnel, self.prenom_personnel, self.contact_personnel,
                                          self.type_personnel)


class AvanceSalaire(models.Model):
    montant_avance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    intitule = models.TextField()
    date_avance = models.DateField(auto_now=True)
    mois_avance = models.CharField(max_length=15, default='Selectionnez', choices=MOIS_CHOICES)
    anscolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    idpersonnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {} '.format(self.idpersonnel, self.intitule, str(self.montant_avance), self.mois_avance)

    @property
    def personnel(self):
        return self.idpersonnel

    @property
    def annee(self):
        return self.anscolaire

class ContratTravail(models.Model):
    date_debut = models.DateField(auto_now=True)
    date_fin = models.DateField(auto_now=True)
    periode_essai = models.CharField(max_length=10)
    thoraire = models.DecimalField(max_digits=10, decimal_places=2)
    salfixe = models.DecimalField(max_digits=10, decimal_places=2)
    duree_contrat_chiffre = models.IntegerField(default=1)
    duree_contrat_lettre = models.CharField(max_length=50)
    date_signature_contrat = models.DateField(auto_now=True)
    idpersonnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {} {}'.format(self.idpersonnel, self.date_debut, self.date_fin, self.periode_essai,
                                       self.duree_contrat_lettre)

    @property
    def personnel(self):
        return self.idpersonnel


class Salaire(models.Model):
    date_paiement = models.DateField(auto_now=True)
    nbre_heure = models.IntegerField(default=0)
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    mois_paie = models.CharField(max_length=15, default='Selectionnez', choices=MOIS_CHOICES)
    detail_paiement = models.TextField()
    taux_horaire = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avance_paie = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    primes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salbrut = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cotis_sociale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salnet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nb_hsupp = models.IntegerField(default=0)
    mont_hsupp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    idpersonnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {}'.format(self.idpersonnel, self.detail_paiement, self.mois_paie)

    @property
    def enseignant(self):
        return self.idpersonnel

    @property
    def annee(self):
        return self.anneescolaire
