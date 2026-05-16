'''RDMO optionset providers for the Publication documentation catalog.

Implements the provider that searches MaRDI Portal and Wikidata for publication
items to let users look up and attach existing publications to their project.

Provides:

- :class:`Publication` — searches external sources for publication items;
  refreshes questionnaire fields upon selection, no creation
'''
# pylint: disable=too-few-public-methods  # Provider subclasses only need get_options

from rdmo.options.providers import Provider
from ..getters import get_items
from ..queries import query_sources

_ITEMS = get_items()

class Publication(Provider):
    '''Publication Provider (MaRDI Portal / Wikidata),
       No User Creation, Refresh Upon Selection
    '''

    search = True
    refresh = True

    def get_options(self, project, search=None, user=None, site=None):
        '''Query external knowledge-graph source(s) and return matching options.

        Args:
            project: RDMO project instance (unused).
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
            item_class = [
                _ITEMS['publication'],
                _ITEMS['scholarly article']
            ]
        )
