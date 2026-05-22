'''RDMO optionset providers for the cross-catalog MaRDI search questionnaire.

Each provider queries the MaRDI Portal for a specific entity type and returns
matching options for use in RDMO option sets. All providers require at least
3 characters, search MaRDI only, and do not offer user creation.

Workflow search providers:
- :class:`ResearchField`       — academic disciplines (also used in model search)
- :class:`MathematicalModel`   — mathematical models
- :class:`Algorithm`           — algorithms
- :class:`Software`            — software (also used in algorithm search)
- :class:`Hardware`            — computer hardware
- :class:`Method`              — methods
- :class:`Instrument`          — research tools / instruments
- :class:`DataSet`             — data sets

Model search providers:
- :class:`ResearchField`          — academic disciplines (also used in workflow search)
- :class:`ResearchProblem`        — research problems
- :class:`ComputationalTask`      — computational tasks
- :class:`Formula`                — mathematical expressions / formulas
- :class:`QuantityOrQuantityKind` — quantities and quantity kinds

Algorithm search providers:
- :class:`AlgorithmicProblem` — algorithmic tasks
- :class:`Software`           — software (also used in workflow search)
'''
# pylint: disable=too-few-public-methods  # Provider subclasses only need get_options

from rdmo.options.providers import Provider

from ..getters import get_items
from ..queries import query_sources

_ITEMS = get_items()

class ResearchField(Provider):
    '''Research Field Provider (MaRDI Portal / Wikidata),
       No User Creation, Refresh Upon Selection
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

        return query_sources(
            search = search,
            item_class = [
                _ITEMS['academic discipline']
            ],
            sources = ['mardi'],
            not_found = False
        )

class MathematicalModel(Provider):
    '''Mathematical Model Provider (MaRDI Portal),
       No User Creation, Refresh Upon Selection
    '''

    search = True

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
                _ITEMS['mathematical model']
            ],
            sources = ['mardi'],
            not_found = False
        )


class Algorithm(Provider):
    '''Algorithm Provider (MaRDI Portal),
       No User Creation, Refresh Upon Selection
    '''

    search = True

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
                _ITEMS['algorithm']
            ],
            sources = ['mardi'],
            not_found = False
        )


class Software(Provider):
    '''Software Provider (MaRDI Portal),
       No User Creation, Refresh Upon Selection
    '''

    search = True

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
                _ITEMS['software']
            ],
            sources = ['mardi'],
            not_found = False
        )


class Hardware(Provider):
    '''Hardware Provider (MaRDI Portal),
       No User Creation, Refresh Upon Selection
    '''

    search = True

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
                _ITEMS['computer hardware']
            ],
            sources = ['mardi'],
            not_found = False
        )


class Method(Provider):
    '''Method Provider (MaRDI Portal),
       No User Creation, Refresh Upon Selection
    '''

    search = True

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
                _ITEMS['method']
            ],
            sources = ['mardi'],
            not_found = False
        )


class Instrument(Provider):
    '''Instrument Provider (MaRDI Portal),
       No User Creation, Refresh Upon Selection
    '''

    search = True

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
                _ITEMS['research tool']
            ],
            sources = ['mardi'],
            not_found = False
        )


class DataSet(Provider):
    '''Data Set Provider (MaRDI Portal),
       No User Creation, Refresh Upon Selection
    '''

    search = True

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
                _ITEMS['data set']
            ],
            sources = ['mardi'],
            not_found = False
        )


class ResearchProblem(Provider):
    '''Research Problem Provider (MaRDI Portal),
       No User Creation, Refresh Upon Selection
    '''

    search = True

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
                _ITEMS['research problem']
            ],
            sources = ['mardi'],
            not_found = False
        )


class ComputationalTask(Provider):
    '''Computational Task Provider (MaRDI Portal),
       No User Creation, Refresh Upon Selection
    '''

    search = True

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
                _ITEMS['computational task']
            ],
            sources = ['mardi'],
            not_found = False
        )


class Formula(Provider):
    '''Formula Provider (MaRDI Portal),
       No User Creation, Refresh Upon Selection
    '''

    search = True

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
                _ITEMS['formula']
            ],
            sources = ['mardi'],
            not_found = False
        )


class AlgorithmicProblem(Provider):
    '''Algorithmic Problem Provider (MaRDI Portal),
       No User Creation, Refresh Upon Selection
    '''

    search = True

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
                _ITEMS['algorithmic task']
            ],
            sources = ['mardi'],
            not_found = False
        )


class QuantityOrQuantityKind(Provider):
    '''Quantity / Quantity Kind Provider (MaRDI Portal),
       No User Creation, Refresh Upon Selection
    '''

    search = True

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
                _ITEMS['quantity'],
                _ITEMS['kind of quantity'],
            ],
            sources = ['mardi'],
            not_found = False
        )
