'''RDMO optionset providers for the Workflow documentation catalog.

Each provider class implements ``get_options`` and is referenced from the
workflow catalog configuration. Providers query MaRDI Portal and Wikidata
for entity suggestions covering research disciplines, methods, tasks, hardware,
instruments, data sets, process steps, and related mathematical models.

Provides:

- :class:`MaRDIAndWikidataSearch`  — generic entity search across MaRDI Portal and Wikidata
- :class:`MainMathematicalModel`   — look up the main mathematical model for a workflow
- :class:`Method`                  — numerical/analytical method lookup; refresh on select
- :class:`RelatedMethod`           — method lookup with optional user creation
- :class:`WorkflowTask`            — task/computation step lookup; refresh on select
- :class:`Hardware`                — hardware platform lookup; refresh on select
- :class:`Instrument`              — scientific instrument lookup; refresh on select
- :class:`DataSet`                 — data set lookup; refresh on select
- :class:`RelatedInstrument`       — instrument lookup with optional user creation
- :class:`RelatedDataSet`          — data-set lookup with optional user creation
- :class:`ProcessStep`             — workflow process-step lookup; refresh on select
- :class:`Discipline`              — research discipline lookup sourced from questionnaire answers
'''
# pylint: disable=too-few-public-methods  # Provider subclasses only need get_options

from rdmo.options.providers import Provider
from rdmo.domain.models import Attribute

from ..constants import BASE_URI
from ..getters import get_items, get_data, get_properties, get_questions, get_sparql_query, get_url
from ..helpers import define_setup
from ..queries import query_sources, query_sources_with_user_additions, query_sparql

_ITEMS = get_items()


class MaRDIAndWikidataSearch(Provider):
    '''General Provider (MaRDI Portal / Wikidata),
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

        return query_sources(
            search = search
        )


class MainMathematicalModel(Provider):
    '''Main Mathematical Model Provider (MaRDI Portal),
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

        return query_sources(
            search = search,
            item_class = _ITEMS['mathematical model'],
            sources = ['mardi'],
        )

class Method(Provider):
    '''Method Provider (MaRDI Portal / Wikidata),
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
            item_class = [
                _ITEMS['method'],
                _ITEMS['algorithm']
            ]
        )

class RelatedMethod(Provider):
    '''Method Provider (MaRDI Portal / Wikidata),
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
        if not search:
            return []

        setup = define_setup(
            query_attributes = ['method'],
            creation = True,
            item_class = [
                _ITEMS['method'],
                _ITEMS['algorithm']
            ]
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class WorkflowTask(Provider):
    '''Task Provider (MaRDI Portal),
       User Creation, No Refresh Upon Selection
    '''

    def get_options(self, project, search=None, user=None, site=None):
        '''Query the MaRDI Portal for Computational Tasks linked to the currently selected Model.

        Reads the Model ID from the questionnaire, fetches associated Task
        items via SPARQL, and returns them as options.

        Args:
            project: RDMO project instance used to look up the current model ID.
            search:  Unused (tasks are filtered by model, not free-text).
            user:    Requesting user (unused).
            site:    Current site (unused).

        Returns:
            List of ``{"id": …, "text": …}`` option dicts for matching tasks.
        '''

        questions = get_questions('workflow')
        options = []
        model_id = ''

        values = project.values.filter(
            snapshot = None,
            attribute = Attribute.objects.get(
                uri = f'{BASE_URI}{questions["Model"]["ID"]["uri"]}'
            )
        )

        for value in values:
            model_id = value.external_id

        if not model_id:
            return options

        _, id_value = model_id.split(':')

        query = get_sparql_query('workflow/queries/task_mardi.sparql').format(
            id_value,
            **get_items(),
            **get_properties()
        )

        results = query_sparql(
            query,
            get_url('mardi', 'sparql')
        )

        if not results:
            return options

        if results[0].get('usedBy', {}).get('value'):
            tasks = results[0]['usedBy']['value'].split(' <|> ')
            for task in tasks:
                identifier, label, description = task.split(' || ')
                options.append(
                    {
                        'id': identifier,
                        'text': f'{label} ({description}) [mardi]'
                    }
                )

        return options

class Hardware(Provider):
    '''Hardware Provider (MaRDI Portal / Wikidata),
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
            item_class = _ITEMS['computer hardware'],
        )

class Instrument(Provider):
    '''Instrument Provider (MaRDI Portal / Wikidata),
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
            item_class = _ITEMS['research tool'],
        )

class DataSet(Provider):
    '''Data Set Provider (MaRDI Portal / Wikidata),
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
            item_class = _ITEMS['data set'],
        )

class RelatedInstrument(Provider):
    '''Instrument Provider (MaRDI Portal / Wikidata),
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
        if not search:
            return []

        setup = define_setup(
            creation = True,
            query_attributes = ['instrument'],
            item_class = _ITEMS['research tool'],
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class RelatedDataSet(Provider):
    '''Data Set Provider (MaRDI Portal / Wikidata),
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
        if not search:
            return []

        setup = define_setup(
            creation = True,
            query_attributes = ['data-set'],
            item_class = _ITEMS['data set'],
        )

        return query_sources_with_user_additions(
            search = search,
            project = project,
            setup = setup
        )

class ProcessStep(Provider):
    '''Process Step Provider (MaRDI Portal / Wikidata),
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
            item_class = _ITEMS['process step'],
        )

class Discipline(Provider):
    '''Discipline Provider (MaRDI Portal / Wikidata / MSC),
       No User Creation, Refresh Upon Selection
    '''

    msc = get_data('data/msc2020.json')

    search = True
    refresh = True

    def get_options(self, project, search=None, user=None, site=None):
        '''Query knowledge graphs and the MSC 2020 classification for matching disciplines.

        Args:
            project: RDMO project instance (unused).
            search:  Search string entered by the user; returns empty list when
                     fewer than 3 characters.
            user:    Requesting user (unused).
            site:    Current site (unused).

        Returns:
            Combined, sorted list of up to 30 ``{"id": …, "text": …}`` option dicts
            from MaRDI Portal / Wikidata (``academic discipline`` class) and MSC 2020.
        '''
        if not search or len(search) < 3:
            return []

        # Discipline from Knowledge Graphs
        options = query_sources(
            search = search,
            item_class = _ITEMS['academic discipline'],
            not_found = False,
        )

        # Mathematical Subjects
        options.extend(
            [
                {
                    'id': f"msc:{self.msc[key]['id']}",
                    'text': f"{key} ({self.msc[key]['quote']}) [msc]"
                }
                for key in self.msc if search.lower() in key.lower()
            ]
        )

        return sorted(options, key=lambda option: option['text'].lower())[:30]
