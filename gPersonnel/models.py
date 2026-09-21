from django.db import models
from gAdministration.models import AnneeScolaire

CIVILITE_CHOICES = [
    ('M', 'Monsieur'),  # 0
    ('Mme', 'Madame'),  # 1
    ('Mlle', 'Madémoisselle')  # 2
]

TYPE_PERSONNEL = (
    ('Vacataire', 'Vacataire'),  # 0
    ('Permanent', 'Permanent')  # 1
)

SEXE_PERSONNEL = (
    ('H', 'Homme'),  # 0
    ('F', 'Femme')  # 1
)

CONTRAT_CHOICES = (
    ('CDD', 'Contrat Durée Déterminée-CDD'),  # 0
    ('CDI', 'Contrat Durée Indéterminée-CDI')  # 1
)

MOIS_CHOICES = (
    ('Selectionnez','Sélectionnez'), # 0
    ('janvier','janvier'), # 1
    ('fevrier','fevrier'), # 2
    ('mars','mars'), # 3
    ('avril','avril'), # 4
    ('mai','mai'), # 5
    ('juin','juin'), # 6
    ('juillet','juillet'), # 7
    ('aout','août'), # 8
    ('septembre','septembre'), # 9
    ('octobre','octobre'), # 10
    ('novembre','novembre'), # 11
    ('decembre','décembre') # 12
)

STATUT_MATRIMONIAL = (
    ('Celibatiare','Célibataire'), # 0
    ('Marie','Marié(e)'), # 1
    ('Divorce','Divorcé(e)'), # 2
    ('Veuf','Veuf(ve)'), # 3
)

# Create your models here.
class Personnel(models.Model):
    nom_personnel = models.CharField(max_length=50)
    prenom_personnel = models.CharField(max_length=100)
    civilite = models.CharField(max_length=15, default=CIVILITE_CHOICES[0][0], choices=CIVILITE_CHOICES)
    date_naissance = models.DateField(blank=True)
    lieu_naissance = models.CharField(max_length=70, blank=True, null=True)
    niveau_etude = models.CharField(max_length=50, blank=True, null=True)
    type_personnel = models.CharField(max_length=15, default=TYPE_PERSONNEL[0][0], choices=TYPE_PERSONNEL)
    adresse_personnel = models.CharField(max_length=70, blank=True, null=True)
    contact_personnel = models.CharField(max_length=25)
    fonction_personnel = models.CharField(max_length=35, blank=True, null=True)
    email_personnel = models.EmailField(blank=True, null=True)
    sexe_personnel = models.CharField(max_length=15, default=SEXE_PERSONNEL[0][0], choices=SEXE_PERSONNEL)
    salbase = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True)
    annee_experience = models.CharField(max_length=10, blank=True, null=True)
    contrat_type = models.CharField(max_length=15, default=CONTRAT_CHOICES[0][0], choices=CONTRAT_CHOICES)
    diplome = models.CharField(max_length=25, blank=True, null=True)
    date_embauche = models.DateField(blank=True)
    photo_employe = models.FileField(upload_to='media/photoemploye/', blank=True, null=True)
    etat_matrimonial = models.CharField(max_length=50, default=STATUT_MATRIMONIAL[0][0], choices=STATUT_MATRIMONIAL)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)

    def __str__(self):
        return '{} | {} | {} | {}'.format(self.nom_personnel, self.prenom_personnel, self.contact_personnel,
                                          self.type_personnel)
    @property
    def annee(self):
        return self.annee_scolaire


class AvanceSalaire(models.Model):
    montant_avance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    intitule = models.TextField()
    date_avance = models.DateField(auto_now=True)
    mois_avance = models.CharField(max_length=15, default=MOIS_CHOICES[1][0], choices=MOIS_CHOICES)
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
    date_debut = models.DateField()
    date_fin = models.DateField()
    periode_essai = models.CharField(max_length=10)
    thoraire = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salfixe = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    duree_contrat_chiffre = models.IntegerField(default=1)
    duree_contrat_lettre = models.CharField(max_length=50)
    date_signature_contrat = models.DateField()
    idpersonnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    aneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {} {}'.format(self.idpersonnel, self.date_debut, self.date_fin, self.periode_essai,
                                       self.duree_contrat_lettre)

    @property
    def personnel(self):
        return self.idpersonnel

    @property
    def annee(self):
        return self.aneescolaire


class Salaire(models.Model):
    date_paiement = models.DateField()
    nbre_heure = models.IntegerField(default=0)
    mois_paie = models.CharField(max_length=15, default=MOIS_CHOICES[1][0], choices=MOIS_CHOICES)
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
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {}'.format(self.idpersonnel, self.detail_paiement, self.mois_paie)

    @property
    def personnel(self):
        return self.idpersonnel

    @property
    def annee(self):
        return self.anneescolaire
