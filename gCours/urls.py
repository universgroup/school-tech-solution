from django.urls import path
from .views import *

urlpatterns = [
    path('ajoutmatiere/', enregistrermatiere, name='ajoutmatiere'),
    path('listematiere/', listematiere, name='listematiere'),
    path('editionmatiere/<int:idmat>', editermatiere, name='editionmatiere'),
    path('afficherdetailsmatiere/<int:codemat>', detailsmatiere, name='afficherdetailsmatiere'),
    path('modifiematiere/<int:idmat>', modifiermatiere, name='modifiematiere'),
    path('suppmatiere/<int:idmat>', supprimermatiere, name='suppmatiere'),

]
