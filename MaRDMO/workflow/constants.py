'''Compile-time constants and configuration builders for the Workflow catalog.

Centralises the property URIs, question/item mappings, and publication-order
definitions used by the workflow documentation sub-package at runtime.
Values are loaded once from the RDMO database via the ``getters`` helpers
and then referenced by handlers, providers, and workers.

Provides:

- ``get_uri_prefix_map()`` — returns the ``{prefix: URI}`` map used to expand compact IDs
- ``order_to_publish()``   — returns the ordered list of workflow attributes for portal export
- Module-level constants built from the above
'''

from ..constants import BASE_URI
from ..getters import get_options, get_questions

software_reference_ids = [
    'DOI',
    'SWMATH',
    'SOURCECODE_URL',
    'DESCRIPTION_URL'
]

data_set_reference_ids = [
    'Yes',
    'DOI',
    'URL',
    'No'
]

# URI PREFIX Map
def get_uri_prefix_map():
    '''Build the attribute-URI → section config mapping for the Workflow Documentation.

    Maps each relation attribute URI to the corresponding questionnaire section
    metadata needed to add or hydrate the related entity.

    Returns:
        Dict mapping full RDMO attribute URI strings to dicts with keys
        ``question_set``, ``question_id``, and ``prefix``.
    '''
    questions = get_questions('workflow')
    uri_prefix_map = {
        f'{BASE_URI}{questions["Process Step"]["Input"]["uri"]}': {
            "question_set": f'{BASE_URI}{questions["Data Set"]["uri"]}',
            "question_id": f'{BASE_URI}{questions["Data Set"]["ID"]["uri"]}',
            "prefix": "DS"
        },
        f'{BASE_URI}{questions["Process Step"]["Output"]["uri"]}': {
            "question_set": f'{BASE_URI}{questions["Data Set"]["uri"]}',
            "question_id": f'{BASE_URI}{questions["Data Set"]["ID"]["uri"]}',
            "prefix": "DS"
        },
        f'{BASE_URI}{questions["Process Step"]["Method"]["uri"]}': {
            "question_set": f'{BASE_URI}{questions["Method"]["uri"]}',
            "question_id": f'{BASE_URI}{questions["Method"]["ID"]["uri"]}',
            "prefix": "M"
        },
        f'{BASE_URI}{questions["Process Step"]["Environment-Software"]["uri"]}': {
            "question_set": f'{BASE_URI}{questions["Software"]["uri"]}',
            "question_id": f'{BASE_URI}{questions["Software"]["ID"]["uri"]}',
            "prefix": "S"
        },
        f'{BASE_URI}{questions["Process Step"]["Environment-Instrument"]["uri"]}': {
            "question_set": f'{BASE_URI}{questions["Instrument"]["uri"]}',
            "question_id": f'{BASE_URI}{questions["Instrument"]["ID"]["uri"]}',
            "prefix": "I"
        },
        f'{BASE_URI}{questions["Method"]["Software"]["uri"]}': {
            "question_set": f'{BASE_URI}{questions["Software"]["uri"]}',
            "question_id": f'{BASE_URI}{questions["Software"]["ID"]["uri"]}',
            "prefix": "S"
        },
        f'{BASE_URI}{questions["Method"]["Instrument"]["uri"]}': {
            "question_set": f'{BASE_URI}{questions["Instrument"]["uri"]}',
            "question_id": f'{BASE_URI}{questions["Instrument"]["ID"]["uri"]}',
            "prefix": "I"
        },
        f'{BASE_URI}{questions["Instrument"]["Software"]["uri"]}': {
            "question_set": f'{BASE_URI}{questions["Software"]["uri"]}',
            "question_id": f'{BASE_URI}{questions["Software"]["ID"]["uri"]}',
            "prefix": "S"
        },
        f'{BASE_URI}{questions["Hardware"]["Software"]["uri"]}': {
            "question_set": f'{BASE_URI}{questions["Software"]["uri"]}',
            "question_id": f'{BASE_URI}{questions["Software"]["ID"]["uri"]}',
            "prefix": "S"
        }
    }
    return uri_prefix_map


# Dictionary with list of property names
PROPS = {
    'PS2IDS': ['input_data_set'],
    'PS2ODS': ['output_data_set'],
    'PS2M': ['uses'],
    'PS2PLS': ['platform_software'],
    'PS2PLI': ['platform_instrument'],
    'PS2F': ['field_of_work'],
    'PS2MA': ['msc_id'],
    'M2S': ['implemented_by_software'],
    'M2I': ['implemented_by_instrument'],
    'S2PL': ['programmed_in'],
    'S2DP': ['depends_on_software'],
    'H2CPU': ['cpu'],
    'DS2DT': ['data_type'],
    'DS2RF': ['representation_format']
}

# Order of toPublish Answers
def order_to_publish():
    '''Build an ordered mapping of publishing option keys to ``(rank, option_value)`` tuples.

    Returns:
        Dict ``{"Yes": (0, …), "doi": (1, …), "url": (2, …), "No": (3, …)}``
        where values are resolved RDMO option strings.
    '''
    options = get_options()
    order = {
        'Yes': (0, options['Yes']),
        'doi': (1, options['DOI']),
        'url': (2, options['URL']),
        'No': (3, options['No'])
        }
    return order

#Dictionary For Reproducibility
REPRODUCIBILITY = {
    'mathematical': 'mathematically reproducible research workflow',
    'runtime': 'runtime reproducible research workflow',
    'result': 'result reproducible research workflow',
    'originalplatform': 'original platform reproducible research workflow',
    'otherplatform': 'cross-platform reproducible research workflow'
    }
