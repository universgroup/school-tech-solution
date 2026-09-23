from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
def erreur_403(request, exception=None):
    return render(request, "403.html", status=403)


class ServiceWorkerView(TemplateView):
    template_name = "sw.js"
    content_type = "application/javascript"