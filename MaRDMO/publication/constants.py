'''Compile-time constants for the Publication documentation sub-package.

Defines the property-to-predicate mappings (``PROPS``), item-info dicts
(``ITEMINFOS``, ``CITATIONINFOS``), and lookup tables for journals, authors,
and languages that the publication worker and handlers consume.

These constants are imported directly; no factory functions are needed because
the publication constants do not depend on the live RDMO database state.
'''

PROPS = {
    'P2ME': ['documents','invents','studies','surveys','uses'],
    'P2A': ['analyzes','applies','invents','studies','surveys'],
    'P2BS': ['documents', 'uses']
}

# URI mappings for item infos
ITEMINFOS = {
    "Name": "title",
    "Description": "description"
}

# URI mappings for citation infos
CITATIONINFOS = {
    "Entrytype": "entrytype",
    "Title": "title",
    "Date": "date",
    "Volume": "volume",
    "Issue": "issue",
    "Page": "page"
}

# URI mappings for languages
LANGUAGES = {
    "Language ID": "id",
    "Language Name": "label",
    "Language Description": "description"
}

# URI mappings for journals
JOURNALS = {
    "Journal ID": "id",
    "Journal ISSN": "issn",
    "Journal Name": "label",
    "Journal Description": "description"
}

# URI mappings for author
AUTHORS = {
    "Author ID": "id",
    "Author ORCID": "orcid_id",
    "Author ZBMath": "zbmath_id",
    "Author Wikidata": "wikidata_id",
    "Author Name": "label",
    "Author Description": "description"
}
