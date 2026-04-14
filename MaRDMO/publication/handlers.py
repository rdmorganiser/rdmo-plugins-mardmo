'''Module containing handlers for the Publication documentation sub-package.

Listens to RDMO model signals to keep publication-related questionnaire state
consistent.  For example, cleans up dependent ``Value`` objects when a
publication set entry is deleted.

Provides:

- :class:`Information` — signal receiver class that wires up publication-set
  relations in the questionnaire (``relation`` method)
- ``publication_set_delete`` — ``post_delete`` receiver that removes orphaned
  values when a publication value set is removed
'''

from django.dispatch import receiver
from django.db.models.signals import post_delete

from rdmo.projects.models import Value

from ..constants import BASE_URI
from ..getters import (
    get_items,
    get_mathmoddb,
    get_mathalgodb,
    get_properties,
    get_questions,
    get_sparql_query,
    get_url
)
from ..queries import query_sparql
from ..adders import add_basics, add_references, add_relations_flexible

from .constants import (
    PROPS,
    ITEMINFOS,
    CITATIONINFOS,
    LANGUAGES,
    JOURNALS,
    AUTHORS
)
from .utils import clean_background_data
from .models import Publication


class Information:
    '''Class containing functions, querying external sources for specific
       entities and integrating the related metadata into the questionnaire.'''

    def __init__(self):
        '''Load publication questions, ontology registries, and the base URI.'''
        self.questions = get_questions('publication')
        self.mathalgodb = get_mathalgodb()
        self.mathmoddb = get_mathmoddb()
        self.base = BASE_URI

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

        # For Models: add Publication–Entity Relations
        if catalog.endswith(('mardmo-model-catalog', 'mardmo-model-basics-catalog')):
            add_relations_flexible(
                project   = project,
                data      = data,
                props     = {'keys': PROPS['P2E'], 'mapping': self.mathmoddb},
                index     = {'set_prefix': set_index},
                statement = {
                    'relation': f'{BASE_URI}{publication["P2E"]["uri"]}',
                    'relatant': f'{BASE_URI}{publication["EntityRelatant"]["uri"]}',
                },
            )

        # For Algorithms: add Publication–Algorithm and Publication–Benchmark/Software Relations
        if catalog.endswith('mardmo-algorithm-catalog'):
            add_relations_flexible(
                project   = project,
                data      = data,
                props     = {'keys': PROPS['P2A'], 'mapping': self.mathalgodb},
                index     = {'set_prefix': set_index},
                statement = {
                    'relation': f'{BASE_URI}{publication["P2A"]["uri"]}',
                    'relatant': f'{BASE_URI}{publication["ARelatant"]["uri"]}',
                },
            )
            add_relations_flexible(
                project   = project,
                data      = data,
                props     = {'keys': PROPS['P2BS'], 'mapping': self.mathalgodb},
                index     = {'set_prefix': set_index},
                statement = {
                    'relation': f'{BASE_URI}{publication["P2BS"]["uri"]}',
                    'relatant': f'{BASE_URI}{publication["BSRelatant"]["uri"]}',
                },
            )


@receiver(post_delete, sender=Value)
def publication_set_delete(sender, **kwargs):
    '''Signal handler: delete hidden citation data when a Publication set page is removed.

    Connected to the ``post_delete`` signal on :class:`~rdmo.projects.models.Value`.
    When the deleted value corresponds to the top-level Publication attribute,
    removes all background citation fields (item info, language, journal, author)
    for that set index.

    Args:
        sender: The :class:`~rdmo.projects.models.Value` model class.
        **kwargs: Signal keyword arguments; ``"instance"`` holds the deleted value.
    '''
    instance = kwargs.get("instance", None)
    questions = get_questions('publication')
    if instance and instance.attribute.uri == f'{BASE_URI}{questions["Publication"]["uri"]}':
        clean_background_data(
            key_dict  = ITEMINFOS | CITATIONINFOS | LANGUAGES | JOURNALS | AUTHORS,
            questions = questions["Publication"],
            project   = instance.project,
            snapshot  = instance.snapshot,
            set_index = instance.set_index
        )
