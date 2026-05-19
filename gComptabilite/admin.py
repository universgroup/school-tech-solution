from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Caisse)
admin.site.register(EtatPaiementCoran)
admin.site.register(EtatPaiementRevision)
admin.site.register(EtatPaiementScolarite)
admin.site.register(PaiementCoran)
admin.site.register(PaiementRevision)
admin.site.register(PaiementScolarite)
