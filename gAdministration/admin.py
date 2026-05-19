from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(CycleScolaire)
admin.site.register(Classe)
admin.site.register(AnneeScolaire)
admin.site.register(Ecole)
admin.site.register(Historique)