'''RDMO optionset providers for the Algorithm documentation catalog.

Each provider class implements ``get_options`` and is referenced from the
algorithm catalog configuration. Providers query MaRDI Portal and Wikidata
for entity suggestions and optionally allow to create new
entries or restrict suggestions to previously documented entities.

Provides:

- :class:`Algorithm` — searches external sources for algorithms; refresh on select
- :class:`RelatedAlgorithmWithoutCreation` — algorithm lookup without user creation
- :class:`AlgorithmicProblem` — searches for algorithmic problems; refresh on select
- :class:`RelatedAlgorithmicProblemWithCreation` — problem lookup with user creation
- :class:`RelatedAlgorithmicProblemWithoutCreation` — problem lookup, no creation
- :class:`Benchmark` — searches for benchmarks; refresh on select
- :class:`RelatedBenchmarkWithCreation` — benchmark lookup with user creation
- :class:`RelatedBenchmarkOrSoftwareWithoutCreation` — benchmark/software lookup, no creation
'''
# pylint: disable=too-few-public-methods  # Provider subclasses only need get_options

from rdmo.options.providers import Provider

from ..getters import get_items
from ..helpers import define_setup
from ..queries import query_sources, query_sources_with_user_additions

_ITEMS = get_items()


class Algorithm(Provider):
    '''Algorithm Provider (MaRDI Portal / Wikidata),
       No User Creation, Refresh Upon Selection
    '''

    search = True
    refresh =True

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
            item_class = _ITEMS['algorithm']
        )

class RelatedAlgorithmWithoutCreation(Provider):
    '''Algorithm Provider (MaRDI Portal),
       No User Creation, No Refresh Upon Selection
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
            query_attributes = ['algorithm'],
            sources = ['mardi'],
            item_class = _ITEMS['algorithm']
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class AlgorithmicProblem(Provider):
    '''Algorithmic Problem Provider (MaRDI Portal / Wikidata),
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
            item_class = _ITEMS['algorithmic task']
        )

class RelatedAlgorithmicProblemWithCreation(Provider):
    '''Algorithmic Problem Provider (MaRDI Portal / Wikidata),
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
            query_attributes = ['problem'],
            creation = True,
            item_class = _ITEMS['algorithmic task']
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class RelatedAlgorithmicProblemWithoutCreation(Provider):
    '''Algorithmic Problem Provider (MaRDI Portal),
       No User Creation, No Refresh Upon Selection
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
            query_attributes = ['problem'],
            sources = ['mardi'],
            item_class = _ITEMS['algorithmic task']
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class Benchmark(Provider):
    '''Benchmark Provider (MaRDI Portal / Wikidata),
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
            item_class = _ITEMS['benchmark']
        )

class RelatedBenchmarkWithCreation(Provider):
    '''Benchmark Provider (MaRDI Portal / Wikidata),
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
            query_attributes = ['benchmark'],
            creation = True,
            item_class = _ITEMS['benchmark']
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class RelatedBenchmarkOrSoftwareWithoutCreation(Provider):
    '''Benchmark, Software Provider (MaRDI Portal),
       No User Creation, No Refresh Upon Selection
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
            query_attributes = ['benchmark', 'software'],
            sources = ['mardi'],
            item_class = [
                _ITEMS['benchmark'],
                _ITEMS['software']
            ]
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )
