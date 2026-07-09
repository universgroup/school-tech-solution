from django.urls import path
from .views import *

urlpatterns = [
    path('enregistrereleve/', enregistrereleve, name='enregistrereleve'),
    path('chargerlisteclasse/', chargerlisteclasse, name='chargerlisteclasse'),
    path('registrematricule/', registrematricule, name='registrematricule'),
    path('afficherdetailsinscription/<int:pkins>', detailsinscription, name='afficherdetailsinscription'),
    path('editioninscription/<int:pk>', editerinscription, name='editioninscription'),
    path('modifieinscription/<int:idins>/<str:mat>', modifierinscription, name='modifieinscription'),
    path('suppinscription/<int:pkins>', supprimerinscription, name='suppinscription'),
    path('filtrerlistegenerale/', filtrelistegenerale,
         name='filtrerlistegenerale'),
    path('chargeranneecourante/', listeinscritsanneescolairecourante, name='chargeranneecourante'),
    path('filtrerlisteinscrits/', filtrelisteinscrits, name='filtrerlisteinscrits'),
    path('recuinscription/<int:idinsc>', recuinscription, name='recuinscription'),
    path('imprimerecuinscription/<int:idins>', imprimerecuinscription, name='imprimerecuinscription'),
    path('reinscriptioneleve/', chargeranneecycle, name='reinscriptioneleve'),
    path('chargerlisteeleveclasse/', chargerlisteeleveclasse, name='chargerlisteeleveclasse'),
    path('validerreinscription/', validerreinscription, name='validerreinscription'),
    path('recureinscription/<int:idinsc>', recureinscription, name='recureinscription'),
    path('imprimerecureinscription/<int:idins>', imprimerecureinscription,
         name='imprimerecureinscription'),
    path('chargerinfoeleveclasse/', chargerinfoeleveclasse, name='chargerinfoeleveclasse'), # url permettant de charger les prénoms, nom et photo de l'élève lors de la reinscription
    path('listereinscritsanneecourante/',listereinscritsanneescolairecourante,name='listereinscritsanneecourante'),
    path('filtrerlistereinscrits/',filtrelistereinscrits,name='filtrerlistereinscrits'),
]
