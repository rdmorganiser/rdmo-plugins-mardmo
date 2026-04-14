'''Django signal router that dispatches RDMO value saves to MaRDMO handlers.

On every ``value_created`` or ``value_updated`` signal the router checks
whether the project's catalog is a MaRDMO catalog and, if so, looks up the
saved attribute URI in the pre-built ``HANDLER_MAP`` to call the matching
handler method.  The map is assembled once at startup via
:func:`~MaRDMO.builders.build_handler_map`.

Provides:

- ``HANDLER_MAP`` — module-level ``{catalog: {uri: handler}}`` dispatch dict
- ``mardmo_router`` — signal receiver wired to ``value_created`` and ``value_updated``
'''

from django.dispatch import receiver
from rdmo.projects.models import Value
from rdmo.projects.signals import value_created, value_updated
from .builders import build_handler_map

HANDLER_MAP = build_handler_map()

@receiver(value_created, sender=Value)
@receiver(value_updated, sender=Value)
def mardmo_router(sender, instance, update_fields=None, **kwargs):
    """Global post-save router: dispatch Value saves to the correct MaRDMO handler.

    Connected to both ``value_created`` and ``value_updated`` signals.
    Looks up the project catalog and attribute URI in the handler map and
    calls the matching handler, if any.

    Args:
        sender:        Signal sender class (``Value``).
        instance:      The saved :class:`~rdmo.projects.models.Value` instance.
        update_fields: Fields that were updated (unused; present for signal compatibility).
        **kwargs:      Additional signal keyword arguments (unused).
    """

    if not instance:
        return

    catalog = getattr(instance.project, "catalog", None)
    if not catalog or not str(catalog).endswith(
        ("mardmo-model-catalog",
         "mardmo-model-basics-catalog",
         "mardmo-algorithm-catalog",
         "mardmo-interdisciplinary-workflow-catalog")
    ):
        return

    attr_uri = getattr(instance.attribute, "uri", None)
    if not attr_uri:
        return

    catalog_name = str(catalog).rsplit("/", maxsplit = 1)[-1]

    handler = HANDLER_MAP.get(catalog_name, {}).get(attr_uri)
    if handler:
        handler(instance)
