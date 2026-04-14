'''RDMO optionset provider for the cross-catalog MaRDI search questionnaire.

Implements a single provider that searches the MaRDI Portal
for any entity type (models, workflows, algorithms) to let users discover
and reference existing entries from any of the three documentation catalogs.

Provides:

- :class:`MaRDISearch` — unified search across MaRDI Portal;
  no refresh upon selection; no user creation
'''
# pylint: disable=too-few-public-methods  # Provider subclasses only need get_options

from rdmo.options.providers import Provider
from ..queries import query_sources

class MaRDISearch(Provider):
    '''General Provider (MaRDI Portal),
       No User Creation, No Refresh Upon Selection
    '''

    search = True

    def get_options(self, project, search=None, user=None, site=None):
        '''Query the MaRDI Portal and return matching options.

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

        # Define the query sources
        sources = ['mardi']

        return query_sources(search, sources)
    