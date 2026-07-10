from django.db import models
from gComptabilite.models import *
from gPersonnel.models import Personnel, MOIS_CHOICES

# Create your models here.
class Matiere(models.Model):
    nom_matiere = models.CharField(max_length=50)
    coeff = models.IntegerField(default=1)

    def __str__(self):
        return '{} {} '.format(self.nom_matiere, self.coeff)


class Cours(models.Model):
    nbre_heure_cour = models.IntegerField()
    jour = models.CharField(max_length=10)
    heure_debut = models.TimeField(auto_now=True)
    heure_fin = models.TimeField(auto_now=True)
    idpersonnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    idmatiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {}'.format(self.idpersonnel, self.idmatiere, self.nbre_heure_cour, self.jour)

    @property
    def enseignant(self):
        return self.idpersonnel

    @property
    def matiere(self):
        return self.idmatiere


class Absence(models.Model):
    nbre_heure_absence = models.IntegerField()
    motif_absence = models.CharField(max_length=50)
    type_motif = models.CharField(max_length=20)
    date_absence = models.DateField()
    mois_absence = models.CharField(max_length=15, default='Selectionnez', choices=MOIS_CHOICES)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    idcours = models.ForeignKey(Cours, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {}'.format(self.idcours, self.motif_absence, self.date_absence, self.mois_absence)

    @property
    def cours(self):
        return self.idcours

    @property
    def annee(self):
        return self.annee_scolaire
