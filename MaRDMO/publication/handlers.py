'''Module containing handlers for the Publication documentation sub-package.

Listens to RDMO model signals to keep publication-related questionnaire state
consistent.  For example, cleans up dependent ``Value`` objects when a
publication set entry is deleted.

Provides:

- :class:`Information` — signal receiver class with ``citation`` and
  ``publication_delete`` handler methods; routed via ``router.py``
'''

from dataclasses import replace

from ..constants import BASE_URI
from ..getters import (
    get_items,
    get_properties,
    get_publication_mapping,
    get_questions,
    get_sparql_query,
    get_url
)
from ..queries import query_sparql
from ..adders import add_basics, add_references, add_relations_flexible

from .constants import (
    PROPS,
    ROUTING,
    ITEMINFOS,
    CITATIONINFOS,
    LANGUAGES,
    JOURNALS,
    AUTHORS
)
from .utils import clean_background_data
from .models import Publication


def _filter_pub_by_class(data, class_set):
    '''Return a copy of *data* with every relation field filtered to entities in *class_set*.'''
    fields = ['analyzes', 'applies', 'documents', 'invents', 'studies', 'surveys', 'uses']
    return replace(data, **{
        f: [v for v in getattr(data, f) if v.item_class in class_set]
        for f in fields
    })


class Information:
    '''Class containing functions, querying external sources for specific
       entities and integrating the related metadata into the questionnaire.'''

    def __init__(self):
        '''Load publication questions, publication role mapping, and the base URI.'''
        self.questions           = get_questions('publication')
        self.publication_mapping = get_publication_mapping()
        self.base                = BASE_URI

    def citation(self, instance):
        '''Handle a Publication ID-field save: populate citation metadata from the
        MaRDI Portal or Wikidata.

        Extracts project, text, external_id, set_index, catalog, and snapshot
        from *instance* and delegates to :meth:`fill_citation`.

        Args:
            instance: RDMO :class:`~rdmo.projects.models.Value` that was just saved.
        '''
        self.fill_citation(
            project     = instance.project,
            text        = instance.text,
            external_id = instance.external_id,
            set_index   = instance.set_index,
            catalog     = str(getattr(instance.project, 'catalog', '')),
            snapshot    = instance.snapshot,
        )

    def fill_citation(self, project, text, external_id, set_index, catalog='', snapshot=None):
        '''Populate publication citation metadata from the MaRDI Portal or Wikidata.

        Cleans any previously stored background data, then (if *text* is set
        and not ``"not found"``) adds basic label/description, fetches SPARQL
        citation data, stores references, and writes catalog-specific
        Publication–Entity / Publication–Algorithm / Publication–Benchmark/Software
        relations.

        Args:
            project:     RDMO project instance.
            text:        Raw ID-field text (``"Label (Description) [source]"``).
            external_id: External ID string in ``"source:id"`` format.
            set_index:   Set-index of the publication page.
            catalog:     Active catalog URI string (used for relation dispatch).
            snapshot:    RDMO snapshot (``None`` for the current snapshot).
        '''

        publication = self.questions["Publication"]

        clean_background_data(
            key_dict  = ITEMINFOS | CITATIONINFOS | LANGUAGES | JOURNALS | AUTHORS,
            questions = publication,
            project   = project,
            snapshot  = snapshot,
            set_index = set_index
        )

        # Stop if no Text or 'not found' in ID Field
        if not text or text == 'not found':
            return

        # Add basic Information
        add_basics(
            project   = project,
            text      = text,
            questions = self.questions,
            item_type = 'Publication',
            index     = (set_index, 0)
        )

        # Get Source and ID of selected Publication
        source, identifier = external_id.split(':')

        # Query the External Source
        query = get_sparql_query(
            f'publication/queries/doi_from_{source}.sparql'
        ).format(
            identifier,
            **get_items(),
            **get_properties()
        )

        results = query_sparql(query, get_url(source, 'sparql'))

        if not results:
            return

        # Structure the data
        data = Publication.from_query(results)

        add_references(
            project   = project,
            data      = data,
            uri       = f'{BASE_URI}{publication["Reference"]["uri"]}',
            set_index = set_index
        )

        if source != 'mardi':
            return

        catalog_slug = catalog.rsplit('/', 1)[-1]
        items        = get_items()

        for rule in ROUTING.get(catalog_slug, []):
            class_set = {f"mardi:{items[c]}" for c in rule['classes']}
            add_relations_flexible(
                project   = project,
                data      = _filter_pub_by_class(data, class_set),
                props     = {'keys': PROPS[rule['props']], 'mapping': getattr(self, rule['mapping'])},
                index     = {'set_prefix': set_index},
                statement = {
                    'relation': f'{BASE_URI}{publication[rule["relation"]]["uri"]}',
                    'relatant': f'{BASE_URI}{publication[rule["relatant"]]["uri"]}',
                },
            )


    def publication_delete(self, instance):
        '''Handle Publication set deletion: remove hidden citation background data.

        Called by the post-delete router when a Value for the top-level Publication
        set attribute is deleted.  Removes all background citation fields (item info,
        language, journal, author) for the deleted set index.

        Args:
            instance: RDMO :class:`~rdmo.projects.models.Value` that was just deleted.
        '''
        clean_background_data(
            key_dict  = ITEMINFOS | CITATIONINFOS | LANGUAGES | JOURNALS | AUTHORS,
            questions = self.questions["Publication"],
            project   = instance.project,
            snapshot  = instance.snapshot,
            set_index = instance.set_index
        )
