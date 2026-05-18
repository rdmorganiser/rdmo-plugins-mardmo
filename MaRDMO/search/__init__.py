"""Search sub-package for MaRDMO.

Provides search functionality across mathematical models, algorithms, and
interdisciplinary workflows stored in the MaRDI Portal:

- :mod:`~MaRDMO.search.providers` — RDMO option set providers for all
  searchable entity types (research fields, models, algorithms, software,
  hardware, methods, instruments, data sets, research problems, computational
  tasks, formulas, algorithmic tasks, quantities and quantity kinds).
- :mod:`~MaRDMO.search.worker` — Background worker that builds and executes
  SPARQL queries for the three search modes (workflow, model, algorithm) and
  returns matching portal items.
- :mod:`~MaRDMO.search.sparql` — Parameterised SPARQL query templates and
  filter fragments for all three search modes, assembled at runtime.
"""
