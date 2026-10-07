from django.urls import path
from .views import *

urlpatterns = [
    path('ajouterpersonnel/', ajouterpersonnel, name='ajouterpersonnel'),
    path('editionpersonnel/<int:idpers>', editerpersonnel, name='editionpersonnel'),
    path('afficherdetailspersonnel/<int:idpers>', detailspersonnel, name='afficherdetailspersonnel'),
    path('modifiepersonnel/<int:idpers>', modifierpersonnel, name='modifiepersonnel'),
    path('supppersonnel/<int:pk>', supprimerpersonnel, name='supppersonnel'),
    path('listegeneralepersonnel/', listepersonnel, name='listegeneralepersonnel'),
    path('listepersonnelcategorie/',listepersonnelcategorie, name='listepersonnelcategorie'),
    path('rapport/personnel/general/', rapportgeneralpersonnel, name='rapportgeneral'),
    path('rapport/personnel/categorie/', rapportpersonnelcategorie, name='rapportcategorie'),
    path('chargerinfosemploye/', chargerinfoemploye, name='chargerinfosemploye'),

    path('enregistrersalaire/', enregistrersalaire, name='enregistrersalaire'),
    path('listesalairemensuel/',listemensuellesalaire,name='listesalairemensuel'),
    path('listesalaireperiode/',listeperiodiquesalaire, name='listesalaireperiode'),
    path('editionsalaire/<int:idsal>', editersalaire, name='editionsalaire'),
    path('afficherdetailsalaire/<int:idsal>', detailssalaire, name='afficherdetailsalaire'),
    path('modifiersalaire/<int:idsal>', modifiersalaire, name='modifiersalaire'),
    path('supprimersalaire/<int:pk>', supprimersalaire, name='supprimersalaire'),
    path('recubulletinsalaire/<int:idsal>', recubulletinsalaire, name='recubulletinsalaire'),
    path('imprimerbulletinsalaire/<int:idsal>', imprimebulletinsalaire, name='imprimerbulletinsalaire'),
    path('chargerinfospersonnel/', charger_infospersonnel, name='chargerinfospersonnel'),
    path('confirmerimpression/<int:id>', confirmerimpression, name='confirmerimpression'),

    path('valideravancesalaire/', valideravancesalaire, name='valideravancesalaire'),
    path('listeavancemensuelle/', listeavancesalaire, name='listeavancemensuelle'),
    path('filtreavancesalaire/',filtrelisteavancesalaire, name='filtreavancesalaire'),
    path('editionavancesalaire/<int:idavsal>', editeravancesalaire, name='editionavancesalaire'),
    path('afficherdetailavancesalaire/<int:idavsal>', detailsavancesalaire, name='afficherdetailavancesalaire'),
    path('modifieravancesalaire/<int:idavsal>', modifieravancesalaire, name='modifieravancesalaire'),
    path('supprimeravancesalaire/<int:pk>', supprimeravancesalaire, name='supprimeravancesalaire'),
    path('recuavancesalaire/<int:idavance>', recubonavancesalaire, name='recuavancesalaire'),
    path('imprimerecuavancesalaire/<int:idavce>', imprimerecuavancesalaire, name='imprimerecuavancesalaire'),

]
