"""Publication Documentation sub-package for MaRDMO.

Provides everything needed to retrieve and document publications within RDMO:

- :mod:`~MaRDMO.publication.models` — Dataclasses for Author, Journal, and
  Publication entities populated from SPARQL results, Crossref, DataCite,
  DOI resolution, zbMath, and ORCID APIs.
- :mod:`~MaRDMO.publication.handlers` — Signal handlers that fetch
  publication metadata and fill the questionnaire when a citation ID is saved.
- :mod:`~MaRDMO.publication.providers` — RDMO optionset provider for searching
  publications across MaRDI Portal and Wikidata.
- :mod:`~MaRDMO.publication.worker` — Background worker that retrieves full
  publication metadata (authors, journals) and writes it to the questionnaire.
- :mod:`~MaRDMO.publication.utils` — Helper functions for querying external
  citation APIs, resolving ORCiDs, and cleaning bibliographic data.
- :mod:`~MaRDMO.publication.constants` — Field mappings and relation lists used
  when writing publication data to the questionnaire and the MaRDI Portal.
"""
