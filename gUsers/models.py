# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

DIRECTEUR_GENERAL = 'DG'
DIRECTEUR_ETUDE = 'DE'
SERVICE_SCOLARITE = 'SCOL'
COMPTABLE = 'COMPTA'
ENSEIGNANT = 'ENS'

NIVEAU_ACCES_CHOICES = (
    (DIRECTEUR_GENERAL, 'Directeur Général'), # 0 Accès à toutes les fonctionnalités
    (DIRECTEUR_ETUDE,'Directeur des Etudes'), # 1 Accès à la gestion des matières, la saisie des notes, l'edition des bulletins et des résultats
    (SERVICE_SCOLARITE, 'Service Scolarité'), # 2 Accès à l'inscription, la reinscription, la caisse, la cantine, les dépenses,
    (COMPTABLE, 'Comptable'), # 2 Accès à l'inscription, la reinscription, la caisse, la cantine, les dépenses, les paiements de scolarité
    (ENSEIGNANT, 'Enseignant'), # 3 Accès seulement à la saisie des notes, les bulletins de notes, les resultats, ne peut rien modifier
)

class Utilisateur(AbstractUser):
    email = models.EmailField(unique=True)   # on force l'unicité, car on va se connecter par email
    photo_profil = models.FileField(upload_to='media/photos_profil/', blank=True, null=True)
    niveau_acces = models.CharField(max_length=10, choices=NIVEAU_ACCES_CHOICES, default=DIRECTEUR_GENERAL)

    USERNAME_FIELD = 'email'          # connexion par email au lieu de username
    REQUIRED_FIELDS = ['username']    # username reste requis pour createsuperuser, mais pas pour se connecter

    def __str__(self):
        return f"{self.get_full_name() or self.username} — {self.get_niveau_acces_display()}"

    # def est_directeur_general(self):
    #     return self.is_superuser or self.niveau_acces == self.DIRECTEUR_GENERAL