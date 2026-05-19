from django.urls import path
from .views import *

# app_name = 'gAdministration'
urlpatterns = [
    path('ajoutclasse/', enregistrerclasse, name='ajoutclasse'),
    path('listeclasse/', listeclasse, name='listeclasse'),
    path('editionclasse/<int:idclas>', editerclasse, name='editionclasse'),  # Permet d'ouvrir juste le
    # # formulaire d'edition de la classe
    path('modifieclasse/<int:idclasse>', modifierclasse, name='modifieclasse'),
    # Permet de valider les MAJ
    # # d'une classe
    path('afficherdetailsclasse/<int:pk>', detailsclasse, name='afficherdetailsclasse'),
    path('suppclasse/<int:idclasse>', supprimerclasse, name='suppclasse'),

    path('ajouteranneescolaire/', ajouteranneescolaire, name='ajouteranneescolaire'),
    path('listeanneescolaire/', listeanneescolaire, name='listeanneescolaire'),
    path('editionanneesc/<int:idanne>', editeranneescolaire, name='editionanneesc'),
    path('afficherdetailsansc/<int:idans>', detailsanneescolaire, name='afficherdetailsansc'),
    path('modifieanneescolaire/<int:idanne>', modifieranneescolaire, name='modifieanneescolaire'),
    path('suppanneescolaire/<int:pk>', supprimeranneescolaire, name='suppanneescolaire'),

    path('ajoutcycle/', enregistrercycle, name='ajoutcycle'),
    path('afficherdetailscycle/<int:pk_cycle>', detailscyclescolaire, name='afficherdetailscycle'),
    path('editioncycle/<int:pk>', editercyclescolaire, name='editioncycle'),
    path('modifiecycle/<int:idcycle>', modifiercyclescolaire, name='modifiecycle'),
    path('suppcycle/<int:idc>', supprimercyclescolaire, name='suppcycle'),
    path('listecycle/', listecyclescolaire, name='listecycle'),

    path('ajoutinfosecole/', enregistrerinfosecole, name='ajoutinfosecole'),
    path('afficherdetailsecole/<int:idec>', detailsinfosecole, name='afficherdetailsecole'),
    path('editioninfosecole/<int:pk>', editerinfosecole, name='editioninfosecole'),
    path('modifieinfosecole/<int:idec>', modifierinfosecole, name='modifieinfosecole'),
    path('listeinfos/', listeinfosecole, name='listeinfos'),

]
