"""Search sub-package for MaRDMO.

Provides search functionality across mathematical models, algorithms, and
interdisciplinary workflows stored in the MaRDI Portal:

- :mod:`~MaRDMO.search.providers` — RDMO option provider (:class:`MaRDISearch`)
  for searching the MaRDI Portal from any questionnaire field.
- :mod:`~MaRDMO.search.worker` — Background worker that executes structured
  SPARQL queries against the MaRDI Portal and returns ranked matches for
  models, workflows, and algorithms.
- :mod:`~MaRDMO.search.sparql` — Parameterised SPARQL query templates and
  filter fragments assembled at runtime for the portal search.
"""
