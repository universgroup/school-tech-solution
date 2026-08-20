# gUsers/decorators.py
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .permissions import (
    PERMISSIONS,
    peut_modifier_note,
    peut_annuler_operation,
    peut_modifier_operation,
)


def action_requise(cle):
    """
    Décorateur générique pour toute permission statique (menu ou action
    sans objet précis).
    Usage : @action_requise('compta_ajouter')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.niveau_acces not in PERMISSIONS.get(cle, []):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def note_modifiable_requis(view_func):
    """
    Protège une vue de modification de note : vérifie le niveau ET
    la date limite de saisie de la période liée à la note.
    La vue doit recevoir 'pk' en paramètre d'URL.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, pk, *args, **kwargs):
        from gNotes.models import Evaluation
        note = get_object_or_404(Evaluation, pk=pk)
        if not peut_modifier_note(request.user, note):
            raise PermissionDenied
        return view_func(request, pk, *args, **kwargs)
    return _wrapped_view


def operation_annulable_requis(view_func):
    """
    Protège la vue d'annulation d'une opération de caisse : vérifie
    le niveau, l'état (non déjà annulée) et l'absence de clôture mensuelle.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, pk, *args, **kwargs):
        from gComptabilite.models import Caisse
        operation = get_object_or_404(Caisse, pk=pk)
        if not peut_annuler_operation(request.user, operation):
            raise PermissionDenied
        return view_func(request, pk, *args, **kwargs)
    return _wrapped_view


def operation_modifiable_requis(view_func):
    """
    Protège la vue de correction d'une opération de caisse : mêmes règles
    que l'annulation (pas de correction sur un mois clôturé ni une
    opération déjà annulée).
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, pk, *args, **kwargs):
        from gComptabilite.models import Caisse
        operation = get_object_or_404(Caisse, pk=pk)
        if not peut_modifier_operation(request.user, operation):
            raise PermissionDenied
        return view_func(request, pk, *args, **kwargs)
    return _wrapped_view
