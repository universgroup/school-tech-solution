from django.urls import path
from .views import *

urlpatterns = [
    path('enregistrercaisserecette/', enregistrer_recette, name='enregistrercaisserecette'),
    path('listerecette/', listerecette, name='listerecette'),
    path('afficherdetailscaisserecette/<int:idcais>', detailscaisserecette,
         name='afficherdetailscaisserecette'),
    path('editioncaisserecette/<int:idcais>', editercaisserecette, name='editioncaisserecette'),
    path('modifiecaisserecette/<int:idcais>', modifiercaisserecette, name='modifiecaisserecette'),
    path('supprimecaisserecette/<int:pk>', supprimercaisserecette, name='supprimecaisserecette'),
    path('rechercherrecette/', recherchersituationrecette, name='rechercherrecette'),

    path('enregistrerdepense/', enregistrerdepense, name='enregistrerdepense'),
    path('listedepense/', listedepense, name='listedepense'),
    path('detailsdepense/<int:id>', detailsdepense, name='detailsdepense'),
    path('editiondepense/<int:id>', editerdepense, name='editiondepense'),
    path('modifiedepense/<int:pk>', modifierdepense, name='modifiedepense'),
    path('supprimedepense/<int:pk>', supprimerdepense, name='supprimedepense'),
    path('rechercherdepense/', recherchersituationdepense, name='rechercherdepense'),

    path('chargerlisteclassepaie/', chargerlisteclassepaiement, name='chargerlisteclassepaie'),
    path('chargerlisteelevepaie/', chargerlisteelevepaiement, name='chargerlisteelevepaie'),
    path('chargerinfoelevepaie/', chargerinfoeleveclasse, name='chargerinfoelevepaie'), # url permettant de charger les prénoms, nom et photo, etc. de l'élève lors du paiement de la scolarité
    path('paiementscolarite/',validerpaiementscolarite,name='paiementscolarite'),
    path('recupaiementscolarite/<int:idetat>/<str:nom_tranche>/<str:mont_paye>',recupaiementscolarite,name='recupaiementscolarite'),
    path('imprimerecuscolarite/<int:idetat>/<str:nom_tranche>/<str:mont_paye>',imprimerecuscolarite, name='imprimerecuscolarite'),
    path('listepaiemensuel/',listepaiementmensuel, name='listepaiemensuel'),
    path('filtrerlistepaieclasse/',filtrelistepaiementclasse, name='filtrerlistepaieclasse'),
    path('detailspaiement/<int:idpaie>',detailpaiementscolaire,name='detailspaiement'),
    path('editionpaiement/<int:idpaie>',editerpaiementscolaire,name='editionpaiement'),
    path('modifierpaiement/<int:idpaie>',modifieretatpaiement, name='modifierpaiement'),
    path('supprimerpaiement/<int:idpaie>',supprimerpaiementscolaire, name='supprimerpaiement'),


]
