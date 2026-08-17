# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    DIRECTEUR_GENERAL = 'DG'
    SERVICE_SCOLARITE = 'SCOL'
    COMPTABLE = 'COMPTA'
    ENSEIGNANT = 'ENS'

    NIVEAU_ACCES_CHOICES = [
        (DIRECTEUR_GENERAL, 'Directeur Général'), # 0
        (SERVICE_SCOLARITE, 'Service Scolarité'), # 1
        (COMPTABLE, 'Comptable'), # 2
        (ENSEIGNANT, 'Enseignant'), # 3
    ]

    email = models.EmailField(unique=True)   # on force l'unicité, car on va se connecter par email
    photo_profil = models.FileField(upload_to='photos_profil/', blank=True, null=True)
    niveau_acces = models.CharField(max_length=10, choices=NIVEAU_ACCES_CHOICES, default=ENSEIGNANT)

    USERNAME_FIELD = 'email'          # connexion par email au lieu de username
    REQUIRED_FIELDS = ['username']    # username reste requis pour createsuperuser, mais pas pour se connecter

    def __str__(self):
        return f"{self.get_full_name() or self.username} — {self.get_niveau_acces_display()}"

    def est_directeur_general(self):
        return self.is_superuser or self.niveau_acces == self.DIRECTEUR_GENERAL