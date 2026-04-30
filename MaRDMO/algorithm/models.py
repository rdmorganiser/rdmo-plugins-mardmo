'''Dataclasses that represent entities in the Algorithm documentation catalog.

Each class maps to one entity type collected from MaRDI Portal and Wikidata during
algorithm documentation. Instances are populated from SPARQL query results and
carry the fields needed to render questionnaire answers and export entries.

Provides:

- :class:`Benchmark`  — benchmark problem associated with an algorithm
- :class:`Software`   — software implementation of an algorithm
- :class:`Problem`    — algorithmic problem solved by an algorithm
- :class:`Algorithm`  — re-exported from :mod:`MaRDMO.models`
'''

from dataclasses import dataclass, field

from .constants import software_reference_ids, benchmark_reference_ids

from ..getters import get_options
from ..helpers import split_value
from ..models import Relatant

@dataclass
class Benchmark:
    '''Data Class For Benchmark Item'''
    reference: dict[int, list[str]] = field(default_factory=dict)
    publications: list[Relatant] = field(default_factory=list)

    @classmethod
    def from_query(cls, raw_data: dict) -> 'Benchmark':
        '''Generate Class Item From Query (single-item, backward-compatible).'''
        return cls.from_query_single(raw_data[0])

    @classmethod
    def from_query_batch(cls, raw_data: list) -> 'dict[str, Benchmark]':
        '''Parse a batch SPARQL result into {external_id: instance} dict.'''
        return {
            row['qid']['value']: cls.from_query_single(row)
            for row in raw_data
            if row.get('qid', {}).get('value')
        }

    @classmethod
    def from_query_single(cls, data: dict) -> 'Benchmark':
        '''Parse one SPARQL result row into a Benchmark instance.'''
        options = get_options()

        benchmark = {
            # Benchmark Reference (DOI, MORWIKI, URL)
            'reference': {
                idx: [options[prop], data[prop]['value']]
                for idx, prop in enumerate(benchmark_reference_ids)
                if data.get(prop, {}).get('value')
            },
            # Get Publication(s)
            'publications': split_value(
                data = data,
                key = 'publication',
                transform = Relatant.from_query
            )
        }

        return cls(
            **benchmark
        )

@dataclass
class Software:
    '''Data Class for Software Item'''
    reference: dict[int, list[str]] = field(default_factory=dict)
    tested_by: list[Relatant] = field(default_factory=list)
    publications: list[Relatant] = field(default_factory=list)

    @classmethod
    def from_query(cls, raw_data: dict) -> 'Software':
        '''Generate Class Item From Query (single-item, backward-compatible).'''
        return cls.from_query_single(raw_data[0])

    @classmethod
    def from_query_batch(cls, raw_data: list) -> 'dict[str, Software]':
        '''Parse a batch SPARQL result into {external_id: instance} dict.'''
        return {
            row['qid']['value']: cls.from_query_single(row)
            for row in raw_data
            if row.get('qid', {}).get('value')
        }

    @classmethod
    def from_query_single(cls, data: dict) -> 'Software':
        '''Parse one SPARQL result row into a Software instance.'''
        options = get_options()

        software = {
            # Software Reference (DOI, SWMATH, and URL)
            'reference': {
                idx: [options[prop], data[prop]['value']]
                for idx, prop in enumerate(software_reference_ids)
                if data.get(prop, {}).get('value')
            },
            # Related Benchmarks
            'tested_by': split_value(
                data = data,
                key = 'tested_by',
                transform = Relatant.from_query
            ),
            # Get Publication(s)
            'publications': split_value(
                data = data,
                key = 'publication',
                transform = Relatant.from_query
            )
        }

        return cls(
            **software
        )

@dataclass
class Problem:
    '''Data Class for Problem Item'''
    specializes: list[Relatant] = field(default_factory=list)
    specialized_by: list[Relatant] = field(default_factory=list)
    manifests: list[Relatant] = field(default_factory=list)

    @classmethod
    def from_query(cls, raw_data: dict) -> 'Problem':
        '''Generate Class Item From Query (single-item, backward-compatible).'''
        return cls.from_query_single(raw_data[0])

    @classmethod
    def from_query_batch(cls, raw_data: list) -> 'dict[str, Problem]':
        '''Parse a batch SPARQL result into {external_id: instance} dict.'''
        return {
            row['qid']['value']: cls.from_query_single(row)
            for row in raw_data
            if row.get('qid', {}).get('value')
        }

    @classmethod
    def from_query_single(cls, data: dict) -> 'Problem':
        '''Parse one SPARQL result row into a Problem instance.'''

        problem = {
            # Get manifests Statements
            'manifests': split_value(
                data = data,
                key = 'manifests',
                transform = Relatant.from_query
            ),
            # Get specializes Statements
            'specializes': split_value(
                data = data,
                key = 'specializes',
                transform = Relatant.from_query
            ),
            # Get specialized by Statements
            'specialized_by': split_value(
                data = data,
                key = 'specialized_by',
                transform = Relatant.from_query
            ),
        }

        return cls(
            **problem
        )

