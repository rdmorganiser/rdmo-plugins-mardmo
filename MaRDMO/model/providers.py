'''RDMO optionset providers for the Model documentation catalog.

Each provider class implements ``get_options`` and is referenced from the
model catalog configuration. Providers query MaRDI Portal and Wikidata for
entity suggestions and optionally allow to create new
entries or restrict suggestions to already-documented entities.

Provides:

- :class:`Formula` — formula lookup; refresh on select
- :class:`ResearchField` — searches external sources; refresh on select, no creation 
- :class:`RelatedResearchFieldWithCreation` — searches external sources; no refresh on select, creation
- :class:`RelatedResearchFieldWithoutCreation` — searches external sources; no refresh on select, no creation
- :class:`ResearchProblem` — searches external sources; refresh on select, no creation
- :class:`RelatedResearchProblemWithCreation` — searches external sources; no refresh on select, creation
- :class:`RelatedResearchProblemWithoutCreation` — searches external sources; no refresh on select, no creation
- :class:`MathematicalModel` — searches external sources; refresh on select, no creation
- :class:`RelatedMathematicalModelWithoutCreation` — searches external sources; no refresh on select, no creation
- :class:`QuantityOrQuantityKind` — searches external sources; refresh on select, no creation
- :class:`RelatedQuantityWithoutCreation` — searches external sources; no refresh on select, no creation
- :class:`RelatedQuantityKindWithoutCreation` — searches external sources; no refresh on select, no creation
- :class:`RelatedQuantityOrQuantityKindWithCreation` — searches external sources; no refresh on select, creation
- :class:`MathematicalFormulation` — searches external sources; refresh on select, no creation
- :class:`RelatedMathematicalFormulationWithCreation` — searches external sources; refresh on select, creation
- :class:`RelatedMathematicalFormulationWithoutCreation` — searches external sources; not refresh on select, no creation
- :class:`Task` — searches external sources; refresh on select, no creation
- :class:`RelatedTaskWithCreation` — searches external sources; no refresh on select, creation
- :class:`RelatedTaskWithoutCreation` — searches external sources; no refresh on select, no creation
- :class:`RelatedModelEntityWithoutCreation` — generic cross-entity lookup without creation
'''
# pylint: disable=too-few-public-methods  # Provider subclasses only need get_options

from rdmo.options.providers import Provider

from ..getters import get_items
from ..helpers import define_setup
from ..queries import query_sources, query_sources_with_user_additions

_ITEMS = get_items()

class Formula(Provider):
    '''Formula Provider for all sorts of Latex Math.
       Future Potential:
          - render Latex Math while entered
          - definitive safe to automatically extract elements
    '''

    search = True

    def get_options(self, project, search=None, user=None, site=None):
        '''Return the search term verbatim as a single formula option.

        Args:
            project: RDMO project instance (unused).
            search:  LaTeX formula string entered by the user.
            user:    Requesting user (unused).
            site:    Current site (unused).

        Returns:
            List containing one ``{"id": "formula", "text": search}`` dict,
            or an empty list when *search* is empty.
        '''
        return [{'id': 'formula', 'text': search}]

class ResearchField(Provider):
    '''Research Field Provider (MaRDI Portal / Wikidata),
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
            item_class = [
                _ITEMS['academic discipline']
            ]
        )

class RelatedResearchFieldWithCreation(Provider):
    '''Research Field Provider (MaRDI Portal / Wikidata),
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


        # Define the query_setup
        setup = define_setup(
            query_attributes = ['field'],
            creation = True,
            item_class = _ITEMS['academic discipline']
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class RelatedResearchFieldWithoutCreation(Provider):
    '''Research Field Provider (MaRDI Portal),
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


        # Define the query_setup
        setup = define_setup(
            query_attributes = ['field'],
            sources = ['mardi'],
            item_class = _ITEMS['academic discipline']
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class ResearchProblem(Provider):
    '''Research Problem Provider (MaRDI Portal / Wikidata),
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
            item_class = _ITEMS['research problem']
        )

class RelatedResearchProblemWithCreation(Provider):
    '''Research Problem Provider (MaRDI Portal / Wikidata),
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

        # Define the query_setup
        setup = define_setup(
            query_attributes = ['problem'],
            creation = True,
            item_class = _ITEMS['research problem']
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class RelatedResearchProblemWithoutCreation(Provider):
    '''Research Problem Provider (MaRDI Portal),
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


        # Define the query_setup
        setup = define_setup(
            query_attributes = ['problem'],
            sources = ['mardi'],
            item_class = _ITEMS['research problem']
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class MathematicalModel(Provider):
    '''Mathematical Model Provider (MaRDI Portal / Wikidata),
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
            item_class = _ITEMS['mathematical model']
        )

class RelatedMathematicalModelWithoutCreation(Provider):
    '''Mathematical Model Provider (MaRDI Portal / Wikidata),
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


        # Define the query_setup
        setup = define_setup(
            query_attributes = ['model'],
            sources = ['mardi'],
            item_class = _ITEMS['mathematical model']
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class QuantityOrQuantityKind(Provider):
    '''Quantity [Kind] Provider (MaRDI Portal / Wikidata),
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
            item_class = [
                _ITEMS['quantity'],
                _ITEMS['kind of quantity']
            ]
        )

class RelatedQuantityWithoutCreation(Provider):
    '''Quantity Provider (MaRDI Portal),
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


        # Define the query_setup
        setup = define_setup(
            query_attributes = ['quantity'],
            sources = ['mardi'],
            item_class = _ITEMS['quantity']
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class RelatedQuantityKindWithoutCreation(Provider):
    '''Quantity Kind Provider (MaRDI Portal),
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


        # Define the query_setup
        setup = define_setup(
            query_attributes = ['quantity'],
            sources = ['mardi'],
            item_class = _ITEMS['kind of quantity']
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class RelatedQuantityOrQuantityKindWithCreation(Provider):
    '''Quantity [Kind] Provider (MaRDI Portal / Wikidata),
       User Creation, Refresh Upon Selection
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


        # Define the query_setup
        setup = define_setup(
            query_attributes = ['quantity'],
            creation = True,
            item_class = [
                _ITEMS['quantity'],
                _ITEMS['kind of quantity']
            ]
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class MathematicalFormulation(Provider):
    '''Mathematical Formulation Provider (MaRDI Portal / Wikidata),
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
            item_class = _ITEMS['mathematical expression']
        )

class RelatedMathematicalFormulationWithCreation(Provider):
    '''Mathematical Formulation Provider (MaRDI Portal / Wikidata),
       User Creation, Refresh Upon Selection
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


        # Define the query_setup
        setup = define_setup(
            query_attributes = ['formulation'],
            creation = True,
            item_class = _ITEMS['mathematical expression']
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class RelatedMathematicalFormulationWithoutCreation(Provider):
    '''Mathematical Formulation Provider (MaRDI Portal),
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


        # Define the query_setup
        setup = define_setup(
            query_attributes = ['formulation'],
            sources = ['mardi'],
            item_class = _ITEMS['mathematical expression']
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class Task(Provider):
    '''Task Provider (MaRDI Portal / Wikidata),
       No User Creation, Refresh Upon Selection
    '''

    search = True
    refresh =True

    def get_options(self, project, search=None, user=None, site=None):
        '''Query the MathModDB ontology and return matching options.

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
            item_class = _ITEMS['computational task']
        )

class RelatedTaskWithCreation(Provider):
    '''Task Provider (MaRDI Portal / Wikidata),
       User Creation, No Refresh Upon Selection
    '''

    search = True

    def get_options(self, project, search=None, user=None, site=None):
        '''Query the MathModDB ontology and return matching options.

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


        # Define the query_setup
        setup = define_setup(
            query_attributes = ['task'],
            creation = True,
            item_class = _ITEMS['computational task']
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class RelatedTaskWithoutCreation(Provider):
    '''Task Provider (MaRDI Portal),
       No User Creation, No Refresh Upon Selection
    '''

    search = True

    def get_options(self, project, search=None, user=None, site=None):
        '''Query the MathModDB ontology and return matching options.

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


        # Define the query_setup
        setup = define_setup(
            query_attributes = ['task'],
            sources = ['mardi'],
            item_class = _ITEMS['computational task']
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class RelatedModelEntityWithoutCreation(Provider):
    '''Research Field, Research Problem, Mathematical Model,
       Mathematical Formulation, Quantity [Kind], Task Provider 
       (MaRDI Portal / Wikidata), No User Creation, No Refresh Upon Selection
    '''

    search = True

    def get_options(self, project, search=None, user=None, site=None):
        '''Query the MathModDB ontology and return matching options.

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


        # Define the query_setup
        setup = define_setup(
            query_attributes = ['field', 'problem', 'model', 'quantity', 'formulation', 'task'],
            sources = ['mardi'],
            item_class = [
                _ITEMS['academic discipline'],
                _ITEMS['research problem'],
                _ITEMS['mathematical model'],
                _ITEMS['quantity'],
                _ITEMS['kind of quantity'],
                _ITEMS['mathematical expression'],
                _ITEMS['computational task']
            ]
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )
