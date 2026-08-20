# gUsers/templatetags/permissions_tags.py
from django import template

from gUsers.permissions import (
    peut as _peut,
    peut_modifier_note as _peut_modifier_note,
    peut_annuler_operation as _peut_annuler_operation,
    peut_modifier_operation as _peut_modifier_operation,
)

register = template.Library()


@register.simple_tag
def peut(user, cle):
    """{% peut request.user 'compta_ajouter' as ok %}"""
    return _peut(user, cle)


@register.simple_tag
def peut_modifier_note(user, note):
    """{% peut_modifier_note request.user note as ok %}"""
    return _peut_modifier_note(user, note)


@register.simple_tag
def peut_annuler_operation(user, operation):
    """{% peut_annuler_operation request.user operation as ok %}"""
    return _peut_annuler_operation(user, operation)


@register.simple_tag
def peut_modifier_operation(user, operation):
    """{% peut_modifier_operation request.user operation as ok %}"""
    return _peut_modifier_operation(user, operation)
