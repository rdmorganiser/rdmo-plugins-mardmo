'''Package-wide constants and the answer-routing flag map for MaRDMO.

Defines the RDMO base URI, catalog URIs, the shared section-name map
(:data:`SECTION_MAP_BASE`), and :data:`flag_dict` — a mapping from
five-tuple boolean flags to the corresponding :mod:`~MaRDMO.rules`
function used by :func:`~MaRDMO.getters.get_answers` to route each
questionnaire value into the correct position in the answers dict.
'''

from . import rules

#RDMO BASE URI
BASE_URI = 'https://rdmo.mardi4nfdi.de/terms/'

#MaRDMO Catalog URIs
CATALOG_MODEL        = 'https://rdmo.mardi4nfdi.de/terms/questions/mardmo-model-catalog'
CATALOG_MODEL_BASICS = 'https://rdmo.mardi4nfdi.de/terms/questions/mardmo-model-basics-catalog'
CATALOG_ALGORITHM    = 'https://rdmo.mardi4nfdi.de/terms/questions/mardmo-algorithm-catalog'
CATALOG_WORKFLOW     = 'https://rdmo.mardi4nfdi.de/terms/questions/mardmo-interdisciplinary-workflow-catalog'

# Mapping from catalog slug to preview template
CATALOG_TEMPLATE_MAP = {
    'mardmo-model-catalog':                      'MaRDMO/modelTemplate.html',
    'mardmo-model-basics-catalog':               'MaRDMO/modelTemplate-basics.html',
    'mardmo-algorithm-catalog':                  'MaRDMO/algorithmTemplate.html',
    'mardmo-interdisciplinary-workflow-catalog': 'MaRDMO/workflowTemplate.html',
}

#MaRDMO Section Mapt (Base)
SECTION_MAP_BASE = {
    'model':       'Mathematical Model',
    'task':        'Computational Task',
    'formulation': 'Mathematical Expression',
    'quantity':    'Quantity [Kind]',
    'field':       'Academic Discipline',
    'algorithm':   'Algorithm',
    'software':    'Software',
    'benchmark':   'Benchmark',
    'publication': 'Publication',
}

ALGORITHM_PROPS = {
    'A2P':       ['solves'],
    'A2S':       ['implemented_by'],
    'Algorithm': ['has_component', 'component_of', 'has_subclass', 'subclass_of', 'related_to'],
}

flag_dict = {
    (False, False, False, False, False): rules.rule_0,
    (True, False, False, False, False): rules.rule_1,
    (False, True, False, False, False): rules.rule_2,
    (True, True, False, False, False): rules.rule_3,
    (False, True, True, False, False): rules.rule_4,
    (True, False, True, False, False): rules.rule_5,
    (True, True, True, False, False): rules.rule_6,
    (True, False, False, False, True): rules.rule_7,
    (False, True, False, False, True): rules.rule_8,
    (False, False, False, True, False): rules.rule_9,
    (False, False, True, False, False): rules.rule_10,
    (False, False, True, True, False): rules.rule_11,
    (False, True, False, True, False): rules.rule_12,
    (True, False, False, True, False): rules.rule_13,
    (True, True, False, True, False): rules.rule_14,
    (True, False, True, True, False): rules.rule_15,
    (True, True, True, True, False): rules.rule_16,
    (True, True, False, False, True): rules.rule_17
}
