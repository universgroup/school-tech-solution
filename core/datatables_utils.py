from django.db.models import Q

def parse_datatables_params(request, columns_map):
    """
    columns_map : liste ordonnée de tuples (field_lookup, searchable, orderable)
    field_lookup vaut None pour une colonne non filtrable/non triable (Photo, Actions).
    """
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '').strip()

    # Recherche par colonne (générée par vos <input> sous les entêtes)
    column_searches = {}
    for index, (field, searchable, orderable) in enumerate(columns_map):
        if not searchable:
            continue
        valeur = request.GET.get(f'columns[{index}][search][value]', '').strip()
        if valeur:
            column_searches[field] = valeur

    # Tri (une seule colonne triée à la fois, cas standard DataTables)
    order_field = None
    order_dir = 'asc'
    order_column_index = request.GET.get('order[0][column]')
    if order_column_index is not None:
        idx = int(order_column_index)
        field, searchable, orderable = columns_map[idx]
        if orderable and field:
            order_field = field
            order_dir = request.GET.get('order[0][dir]', 'asc')

    return {
        'draw': draw,
        'start': start,
        'length': length,
        'search_value': search_value,
        'column_searches': column_searches,
        'order_field': order_field,
        'order_dir': order_dir,
    }


def appliquer_recherche_globale(queryset, search_value, champs_recherchables):
    if not search_value:
        return queryset
        
    condition = Q()
    for champ in champs_recherchables:
        condition |= Q(**{f'{champ}__icontains': search_value})
    return queryset.filter(condition)


def appliquer_recherches_colonnes(queryset, column_searches):
    for champ, valeur in column_searches.items():
        queryset = queryset.filter(**{f'{champ}__icontains': valeur})
    return queryset


def appliquer_tri(queryset, order_field, order_dir):
    if not order_field:
        return queryset
    prefixe = '-' if order_dir == 'desc' else ''
    return queryset.order_by(f'{prefixe}{order_field}')