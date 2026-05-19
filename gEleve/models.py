from django.db import models
from gAdministration.models import *
import uuid

SEXE_ELEVE_CHOICES = (
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('Masculin', 'Masculin'),  # 1
    ('Feminin', 'Feminin')  # 2
)


# Create your models here.
class Eleve(models.Model):
    ideleve = models.IntegerField(null=True)
    matricule = models.CharField(max_length=50, primary_key=True, unique=True, default=uuid.uuid4)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    sexe_eleve = models.CharField(max_length=15, default=SEXE_ELEVE_CHOICES[1][1], choices=SEXE_ELEVE_CHOICES)
    pere = models.CharField(max_length=50)
    mere = models.CharField(max_length=50, default='')
    tuteur = models.CharField(max_length=50)
    contact_parent = models.CharField(max_length=25)
    email_parent = models.EmailField(blank=True, null=False)
    adresse = models.CharField(max_length=50)
    ecole_origine = models.CharField(max_length=50)
    photo_eleve = models.FileField(upload_to='media/photoeleve/', null=True)
    datenaissance = models.DateField()
    lieu_naissance = models.CharField(max_length=50)
    date_arrivee = models.DateField()
    date_depart = models.DateField(null=True)
    depart = models.BooleanField(default=False)
    pays_naissance = models.CharField(max_length=70)

    def __str__(self):
        return f'{self.matricule}-{self.nom}-{self.prenom}-{self.contact_parent}'


class Discipline(models.Model):
    motif_sanction = models.TextField()
    sanction = models.CharField(max_length=80)
    observation = models.TextField()
    annescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    date_sanction = models.DateField()
    delit = models.TextField()
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {}'.format(self.mateleve, self.motif_sanction, self.sanction, self.delit)

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.annescolaire


class Inscription(models.Model):
    date_inscription = models.DateField(auto_now=True)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    etat_inscription = models.CharField(max_length=10, default='Inscrit')
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idcycle = models.ForeignKey(CycleScolaire, on_delete=models.CASCADE, null=True)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} '.format(self.mateleve, self.idclasse, self.etat_inscription)

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse.nom_classe

    @property
    def annee(self):
        return self.annee_scolaire

    @property
    def cycle(self):
        return self.idcycle.cycle
