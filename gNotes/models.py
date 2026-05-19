from django.db import models
from gEleve.models import Eleve
from gAdministration.models import AnneeScolaire, Classe
from gCours.models import Matiere
from gComptabilite.models import MOIS_CHOICES

TRIMESTRE_CHOICES = (
    ('Selectionnez', 'Sélectionnez'),
    ('MP', 'Maternelle/Primaire'),
    ('1er trimestre', '1er trimestre'),
    ('2ème trimestre', '2ème trimestre'),
    ('3ème trimestre', '3ème trimestre'),
    ('CLGE', 'Collège/Lycée'),
    ('1er semestre', '1er semestre'),
    ('2ème semestre', '2ème semestre')

)


# Create your models here.
class Evaluation(models.Model):
    note1 = models.FloatField(default=0)
    note2 = models.FloatField(default=0)
    note3 = models.FloatField(default=0)
    mois_evaluation = models.CharField(max_length=15, default='Selectionnez', choices=MOIS_CHOICES)
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    trimestre = models.CharField(max_length=15, default='Selectionnez', choices=TRIMESTRE_CHOICES)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)
    idmatiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {} {} '.format(self.mateleve, self.mois_evaluation, self.trimestre, str(self.note1),
                                        str(self.note2))

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def matiere(self):
        return self.idmatiere

    @property
    def annee(self):
        return self.anneescolaire


class ResultatTrimestre(models.Model):
    trimes = models.CharField(max_length=15)
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    mgenerale = models.FloatField(default=0)
    mcours = models.FloatField(default=0)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} '.format(self.mateleve, self.trimes, str(self.mgenerale))

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.anneescolaire


class ResultatAnnuel(models.Model):
    mga = models.FloatField(default=0)
    annes = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.mateleve, str(self.mga))

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.annes
