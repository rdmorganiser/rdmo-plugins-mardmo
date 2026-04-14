'''Base dataclasses shared across all MaRDMO documentation sub-packages.

Provides:

- :class:`Relatant` — a lightweight ``(id, label, description)`` triple used
  to represent any referenced entity (model, software, publication, …).
- :class:`RelatantWithClass` — extends :class:`Relatant` with an
  ``item_class`` field for entities whose Wikibase class matters (e.g.
  quantities that are either ``Quantity`` or ``QuantityKind``).

Both classes expose ``from_query``, ``from_triple``, and (for
:class:`Relatant`) ``from_msc`` class methods for constructing instances
from different data sources.
'''

from dataclasses import dataclass
from typing import Optional

@dataclass
class Relatant:
    '''Data Class For Relatant Items'''
    id: Optional[str]
    label: Optional[str]
    description: Optional[str]

    @classmethod
    def from_query(cls, raw: str) -> 'Relatant':
        '''Construct a :class:`Relatant` from a pipe-delimited query string.

        Args:
            raw: String in the format ``"id || label || description"``.

        Returns:
            New :class:`Relatant` instance.
        '''
        identifier, label, description = raw.split(" || ")
        return cls(
            id = identifier,
            label = label,
            description = description,
        )

    @classmethod
    def from_triple(cls, identifier: str, label: str, description: str) -> 'Relatant':
        '''Construct a :class:`Relatant` from explicit id, label, description arguments.

        Args:
            identifier:  External ID string (e.g. ``"mardi:Q42"``).
            label:       Human-readable label.
            description: Short description.

        Returns:
            New :class:`Relatant` instance.
        '''
        return cls(
            id = identifier,
            label = label,
            description = description,
        )

    @classmethod
    def from_msc(cls, identifier: str, label: str, description: str) -> 'Relatant':
        '''Construct a :class:`Relatant` from an MSC 2020 subject classification entry.

        Args:
            identifier:  MSC subject ID string (without ``msc:`` prefix); the
                         prefix is added automatically.
            label:       Human-readable subject label.
            description: Short description or scope note for the MSC entry.

        Returns:
            New :class:`Relatant` instance with ``id`` set to ``"msc:{identifier}"``.
        '''
        return cls(
            id = f"msc:{identifier}",
            label = label,
            description = description,
        )

@dataclass
class RelatantWithClass:
    '''Data Class For Relatant Items With Class'''
    id: Optional[str]
    label: Optional[str]
    description: Optional[str]
    item_class: Optional[str]

    @classmethod
    def from_query(cls, raw: str) -> 'RelatantWithClass':
        '''Parse a ``||``-delimited SPARQL result string into a RelatantWithClass instance.

        Args:
            raw: String with three or four ``" || "``-separated fields:
                 identifier, label, description, and optionally item_class.

        Returns:
            New :class:`RelatantWithClass` instance; ``item_class`` is ``None``
            when only three fields are present.
        '''
        raw_split = raw.split(" || ")
        if len(raw_split) == 3:
            item_class = None
        else:
            item_class = raw_split[3]
        return cls(
            id = raw_split[0],
            label = raw_split[1],
            description = raw_split[2],
            item_class = item_class
        )
