from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('connexion/', ConnexionView.as_view(), name='connexion'),
    path('deconnexion/', DeconnexionView.as_view(), name='deconnexion'),
    path('liste_utilisateurs/', listeutilisateurs, name='liste_utilisateurs'),
    path('creer_utilisateur/', creerutilisateur, name='creer_utilisateur'),
    path('editionutilisateur/<int:iduser>',editerutilisateur, name='editionutilisateur'),
    path('modifier_utilisateur/<int:pk>', modifierutilisateur, name='modifier_utilisateur'),
    path('mon-profil/<int:iduser>', affichermonprofil, name='mon_profil'),
    path('suppressionutilisateur/<int:iduser>',supprimerutilisateur, name='suppressionutilisateur'),

    # Réinitialisation du mot de passe (flux natif Django, rien à recoder)
    path('mot-de-passe-oublie/', auth_views.PasswordResetView.as_view(
        template_name='gUsers/mot_de_passe_oublie.html',
        email_template_name='emails/reset_mot_de_passe.html',
        subject_template_name='emails/reset_mot_de_passe_sujet.txt',
        success_url='/gestion-utilisateurs/mot-de-passe-oublie/envoye/',
    ), name='password_reset'),

    path('mot-de-passe-oublie/envoye/', auth_views.PasswordResetDoneView.as_view(
        template_name='gUsers/mot_de_passe_oublie_envoye.html'
    ), name='password_reset_done'),

    path('reinitialiser/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='gUsers/reinitialiser_mot_de_passe.html',
        success_url='/gestion-utilisateurs/reinitialiser/complet/',
    ), name='password_reset_confirm'),

    path('reinitialiser/complet/', auth_views.PasswordResetCompleteView.as_view(
        template_name='gUsers/reinitialiser_mot_de_passe_complet.html'
    ), name='password_reset_complete'),
]