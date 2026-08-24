from django.shortcuts import render

# Create your views here.
def erreur_403(request, exception=None):
    return render(request, "403.html", status=403)