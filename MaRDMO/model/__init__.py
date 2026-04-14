"""Model Documentation sub-package for MaRDMO.

Provides everything needed to document mathematical models within RDMO:

- :mod:`~MaRDMO.model.models` — Dataclasses for MathematicalModel, Task,
  MathematicalFormulation, QuantityOrQuantityKind, ResearchField, and
  ResearchProblem entities from MaRDI Portal or Wikidata.
- :mod:`~MaRDMO.model.handlers` — Signal handlers that populate the
  questionnaire when an external ID is saved.
- :mod:`~MaRDMO.model.providers` — RDMO optionset providers for searching models,
  formulations, tasks, quantities, and related entities in external knowledge
  graphs.
- :mod:`~MaRDMO.model.worker` — Background worker for generating model previews
  and exporting model entries to the MaRDI Portal.
- :mod:`~MaRDMO.model.utils` — Utility functions for building quantity info and
  mapping entity-quantity relationships.
- :mod:`~MaRDMO.model.constants` — Relation mappings, data-property definitions,
  and URI-prefix configurations specific to the model catalogs.
"""
