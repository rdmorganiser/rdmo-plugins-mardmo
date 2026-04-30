'''Django signal router that dispatches RDMO value saves and deletes to MaRDMO handlers.

On every ``value_created`` or ``value_updated`` signal the post-save router checks
whether the project's catalog is a MaRDMO catalog and, if so, looks up the
saved attribute URI in ``HANDLER_MAP`` to call the matching handler method.

On every ``post_delete`` signal on ``Value`` the post-delete router does the same
lookup in ``DELETE_HANDLER_MAP``.

Both maps are assembled once at startup via :func:`~MaRDMO.builders.build_handler_map`
and :func:`~MaRDMO.builders.build_delete_handler_map`.

Provides:

- ``HANDLER_MAP``        — ``{catalog: {uri: handler}}`` dispatch dict for saves
- ``DELETE_HANDLER_MAP`` — ``{catalog: {uri: handler}}`` dispatch dict for deletes
- ``mardmo_router_post_save``   — receiver wired to ``value_created`` and ``value_updated``
- ``mardmo_router_post_delete`` — receiver wired to Django's ``post_delete`` on ``Value``
'''

from django.dispatch import receiver
from rdmo.projects.models import Value
from rdmo.projects.signals import value_created, value_updated, value_deleted
from .builders import build_post_save_handler_set, build_post_delete_handler_set

HANDLER_MAP        = build_post_save_handler_set()
DELETE_HANDLER_MAP = build_post_delete_handler_set()

_MARDMO_CATALOGS = (
    "mardmo-model-catalog",
    "mardmo-model-basics-catalog",
    "mardmo-algorithm-catalog",
    "mardmo-interdisciplinary-workflow-catalog",
)


def _catalog_name(instance):
    '''Return the short catalog slug for *instance*, or ``None`` if not a MaRDMO catalog.'''
    catalog = getattr(instance.project, "catalog", None)
    if not catalog or not str(catalog).endswith(_MARDMO_CATALOGS):
        return None
    return str(catalog).rsplit("/", maxsplit=1)[-1]


@receiver(value_created, sender=Value)
@receiver(value_updated, sender=Value)
def mardmo_router_post_save(sender, instance, update_fields=None, **kwargs):  # pylint: disable=unused-argument
    """Post-save router: dispatch Value saves to the correct MaRDMO handler.

    Connected to both ``value_created`` and ``value_updated`` signals.
    Looks up the project catalog and attribute URI in ``HANDLER_MAP`` and
    calls the matching handler, if any.

    Args:
        sender:        Signal sender class (``Value``).
        instance:      The saved :class:`~rdmo.projects.models.Value` instance.
        update_fields: Fields that were updated (unused; present for signal compatibility).
        **kwargs:      Additional signal keyword arguments (unused).
    """
    if not instance:
        return

    catalog_name = _catalog_name(instance)
    if not catalog_name:
        return

    attr_uri = getattr(instance.attribute, "uri", None)
    if not attr_uri:
        return

    handler = HANDLER_MAP.get(catalog_name, {}).get(attr_uri)
    if handler:
        handler(instance)


@receiver(value_deleted, sender=Value)
def mardmo_router_post_delete(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Post-delete router: dispatch Value deletions to the correct MaRDMO handler.

    Connected to RDMO's ``value_deleted`` signal on ``Value``.
    Looks up the project catalog and attribute URI in ``DELETE_HANDLER_MAP`` and
    calls the matching handler, if any.

    Args:
        sender:   Signal sender class (``Value``).
        instance: The deleted :class:`~rdmo.projects.models.Value` instance.
        **kwargs: Additional signal keyword arguments (unused).
    """
    if not instance:
        return

    catalog_name = _catalog_name(instance)
    if not catalog_name:
        return

    attr_uri = getattr(instance.attribute, "uri", None)
    if not attr_uri:
        return

    handler = DELETE_HANDLER_MAP.get(catalog_name, {}).get(attr_uri)
    if handler:
        handler(instance)
