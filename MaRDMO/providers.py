'''General RDMO optionset providers shared across all MaRDMO catalogs.

Provides:

- :class:`Software` — searches MaRDI Portal and Wikidata for software items;
  refreshes questionnaire fields upon selection.
- :class:`RelatedSoftwareWithCreation` — like :class:`Software` but also
  surfaces user-created software entries from the current project and offers
  a "create new" option when the search term is not found.

These providers are catalog-agnostic and are referenced from the model,
algorithm, or workflow catalog configurations.
'''
# pylint: disable=too-few-public-methods  # Provider subclasses only need get_options

from rdmo.options.providers import Provider

from .getters import get_items
from .helpers import define_setup
from .queries import query_sources, query_sources_with_user_additions

_ITEMS = get_items()

class Software(Provider):
    '''Software Provider (MaRDI Portal / Wikidata),
       No User Creation, Refresh Upon Selection
    '''

    search = True
    refresh = True

    def get_options(self, project, search=None, user=None, site=None):
        '''Query external knowledge-graph source(s) and return matching options.

        Args:
            project: RDMO project instance (used for user-entry lookups when applicable).
            search:  Search string entered by the user; returns empty list when
                     fewer than 3 characters.
            user:    Requesting user (unused).
            site:    Current site (unused).

        Returns:
            List of ``{"id": …, "text": …}`` option dicts sorted by relevance.
        '''
        if not search or len(search) < 3:
            return []

        return query_sources(
            search = search,
            item_class = _ITEMS['software'],
        )

class RelatedSoftwareWithCreation(Provider):
    '''Software Provider (MaRDI Portal / Wikidata / MathAlgoDB),
       User Creation, No Refresh Upon Selection
    '''

    search = True

    def get_options(self, project, search=None, user=None, site=None):
        '''Query external knowledge-graph source(s) and return matching options.

        Args:
            project: RDMO project instance (used for user-entry lookups when applicable).
            search:  Search string entered by the user; returns empty list when
                     fewer than 3 characters.
            user:    Requesting user (unused).
            site:    Current site (unused).

        Returns:
            List of ``{"id": …, "text": …}`` option dicts sorted by relevance.
        '''
        if not search or len(search) < 3:
            return []

        setup = define_setup(
            query_attributes = ['software'],
            creation = True,
            item_class = _ITEMS['software'],
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )
