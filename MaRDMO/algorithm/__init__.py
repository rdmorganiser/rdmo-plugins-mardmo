"""Algorithm Documentation sub-package for MaRDMO.

Provides everything needed to document algorithms within RDMO:

- :mod:`~MaRDMO.algorithm.models` — Dataclasses representing Algorithm, Problem,
  Software, and Benchmark entities retrieved from MaRDI Portal or Wikidata.
- :mod:`~MaRDMO.algorithm.handlers` — Signal handlers that populate the
  questionnaire when an external ID is saved.
- :mod:`~MaRDMO.algorithm.providers` — RDMO optionset providers for searching
  algorithms, problems, software, and benchmarks in external knowledge graphs.
- :mod:`~MaRDMO.algorithm.worker` — Background worker for generating algorithm
  previews and exporting algorithm entries to the MaRDI Portal.
- :mod:`~MaRDMO.algorithm.constants` — Relation mappings, section maps, and
  URI-prefix configurations specific to the algorithm catalog.
"""
