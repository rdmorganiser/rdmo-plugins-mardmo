"""Interdisciplinary Workflow Documentation sub-package for MaRDMO.

Provides everything needed to document interdisciplinary research workflows
within RDMO:

- :mod:`~MaRDMO.workflow.models` — Dataclasses for ProcessStep, Method,
  Software, Hardware, and DataSet entities from MaRDI Portal / Wikidata,
  as well as Variables and Parameters.
- :mod:`~MaRDMO.workflow.handlers` — Signal handlers that populate the
  questionnaire when a software, hardware, instrument, data set, method, or
  process-step ID is saved.
- :mod:`~MaRDMO.workflow.providers` — RDMO optionset providers for searching
  software, hardware, instruments, data sets, methods, process steps,
  disciplines, and workflow tasks in external knowledge graphs.
- :mod:`~MaRDMO.workflow.worker` — Background worker for generating workflow
  previews and exporting workflow entries to the MaRDI Portal.
- :mod:`~MaRDMO.workflow.utils` — Helpers for partitioning disciplines,
  extracting data-set size, reference, and archive metadata.
- :mod:`~MaRDMO.workflow.constants` — URI-prefix maps, property lists, and
  reproducibility vocabulary for the workflow catalog.
"""
