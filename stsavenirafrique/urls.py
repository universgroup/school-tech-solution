"""
URL configuration for stsavenirafrique project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

# from . import views # c est une autre methode/facon d'importer les views

from django.conf import settings
from django.conf.urls.static import static
from gUsers.views import home

urlpatterns = [   # Racine du site "/" redirige vers la page de connexion
                  path('', RedirectView.as_view(pattern_name='connexion', permanent=False), name='connexion'),
                  path('accueil/',home,name='accueil'),  
                  path('admin/', admin.site.urls),
                  path('administration/', include('gAdministration.urls'), name='administration'),
                  path('comptabilite/', include('gComptabilite.urls'), name='comptabilite'),
                  #path('cours/', include('gCours.urls'), name='cours'),
                  path('eleves/', include('gEleve.urls'), name='eleves'),
                  # path('notes/', include('gNotes.urls'), name='notes'),
                  # path('personnel/', include('gPersonnel.urls'), name='personnel'),
                  
                  path('utilisateurs/', include('gUsers.urls'), name='utilisateurs'),  # l'attribut name devant chaque url contenant le include n'a pas d'effet, donc facultatif              
                  

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# Handler 403 personnalisé (page affichée quand PermissionDenied est levée)
# À ajouter également dans ce fichier :
handler403 = "core.views.erreur_403"