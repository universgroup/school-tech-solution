from django.urls import path
from .views import *

urlpatterns = [
    path('ajouterpersonnel/', ajouterpersonnel, name='ajouterpersonnel'),
    path('editionpersonnel/<int:idpers>', editerpersonnel, name='editionpersonnel'),
    path('afficherdetailspersonnel/<int:idpers>', detailspersonnel, name='afficherdetailspersonnel'),
    path('modifiepersonnel/<int:idpers>', modifierpersonnel, name='modifiepersonnel'),
    path('supppersonnel/<int:pk>', supprimerpersonnel, name='supppersonnel'),
    path('listegeneralepersonnel/', listepersonnel, name='listegeneralepersonnel'),
    path('enregistrersalaire/', enregistrersalaire, name='enregistrersalaire'),
    path('editionsalaire/<int:idsal>', editersalaire, name='editionsalaire'),
    path('afficherdetailsalaire/<int:idsal>', detailssalaire, name='afficherdetailsalaire'),
    path('modifiersalaire/<int:idsal>', modifiersalaire, name='modifiersalaire'),
    path('supprimersalaire/<int:pk>', supprimersalaire, name='supprimersalaire'),
    path('recubulletinsalaire/<int:idsal>', recubulletinsalaire, name='recubulletinsalaire'),
    path('imprimerbulletinsalaire/<int:idsal>', imprimebulletinsalaire, name='imprimerbulletinsalaire'),
    path('ajouteravancesalaire/', ajouteravancesalaire, name='ajouteravancesalaire'),
    path('editionavancesalaire/<int:idavsal>', editeravancesalaire, name='editionavancesalaire'),
    path('afficherdetailavancesalaire/<int:idavsal>', detailsavancesalaire,
         name='afficherdetailavancesalaire'),
    path('modifieravancesalaire/<int:idavsal>', modifieravancesalaire, name='modifieravancesalaire'),
    path('supprimeravancesalaire/<int:pk>', supprimeravancesalaire, name='supprimeravancesalaire'),
    path('recuavancesalaire/<int:idavance>', recubonavancesalaire, name='recuavancesalaire'),
    path('imprimerecuavancesalaire/<int:idavce>', imprimerecuavancesalaire,
         name='imprimerecuavancesalaire'),

]
