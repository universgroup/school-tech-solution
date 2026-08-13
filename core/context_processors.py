from gAdministration.models import AnneeScolaire, CycleScolaire


def donnees_menu_rapports(request):

    if not request.user.is_authenticated:
        return {}
    return {
        'anneescol': AnneeScolaire.objects.all().order_by('id'),
        'cyclescol': CycleScolaire.objects.all(),
    }