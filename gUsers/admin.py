
# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur


class UtilisateurAdmin(UserAdmin):
    model = Utilisateur
    fieldsets = UserAdmin.fieldsets + (
        ('Informations complémentaires', {'fields': ('photo_profil', 'niveau_acces')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations complémentaires', {'fields': ('email', 'photo_profil', 'niveau_acces')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'niveau_acces', 'is_staff')


admin.site.register(Utilisateur, UtilisateurAdmin)