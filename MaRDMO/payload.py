'''Wikibase REST API payload builder for MaRDMO exports.

Provides :class:`GeneratePayload`, which transforms a prepared answers dict
into a fully structured payload dict ready for posting to the MaRDI Portal:

- Builds ``Item*`` entries for every unique entity (labels, descriptions,
  aliases, statements, qualifiers).
- Builds ``RELATION_*`` entries for cross-item statements that reference
  other items by their temporary ``Item<n>`` placeholder.
- Builds ``ALIAS_*`` entries for alias additions to existing portal items.

Key methods: :meth:`~GeneratePayload.add_data_properties`,
:meth:`~GeneratePayload.add_check_results`,
:meth:`~GeneratePayload.add_aliases`,
:meth:`~GeneratePayload.build_relation_check_query`.
'''

import logging

from dataclasses import dataclass, field
from typing import Optional

import re
import requests

from .queries import query_item

_logger = logging.getLogger(__name__)

@dataclass
class PayloadState:
    '''Data Class to store the current state of the Payload.'''
    counter: int = 0
    dictionary: dict = field(default_factory=dict)
    subject: dict = field(default_factory=dict)
    subject_item: Optional[str] = None

class GeneratePayload:
    '''Class to build the Payload for an Export to a Wikibase
       with Items, Statements, Qualifiers, and Checks.'''

    def __init__(
        self,
        url: str,
        user_items: dict | None = None,
        wikibase: dict | None = None,
        dependency: dict | None = None
    ):
        '''Initialise the payload builder.

        Args:
            url:         Base URL of the target Wikibase instance (e.g.
                         ``"https://portal.mardi4nfdi.de"``).
            user_items:  Mapping of temporary ``"Item<n>"`` keys to item
                         dicts ``{ID, Name, Description}``.  Produced by
                         :func:`~MaRDMO.helpers.unique_items`.
            wikibase:    Wikibase vocabulary dicts.  Expected keys are
                         ``items``, ``properties``, ``relations``, and
                         optionally ``data_properties``.
            dependency:  Dependency graph ``{item_key: set_of_dependencies}``
                         that controls item-creation order during export.
        '''
        # Input Attributes
        self.url: str = url
        self.user_items: dict = user_items
        self.wikibase: dict =  wikibase
        self.dependency: dict= dependency
        # Working Attributes
        self.state: PayloadState = PayloadState()

    def _items_url(self):
        '''Return the Wikibase REST API endpoint URL for creating new items.'''
        return f'{self.url}/w/rest.php/wikibase/v1/entities/items'

    def _statement_url(self, item):
        '''Return the Wikibase REST API endpoint URL for adding statements to *item*.

        Args:
            item: Wikibase QID string (e.g. ``"Q42"``).
        '''
        return f'{self.url}/w/rest.php/wikibase/v1/entities/items/{item}/statements'

    def _alias_url(self, item):
        '''Return the Wikibase REST API endpoint URL for adding English aliases to *item*.

        Args:
            item: Wikibase QID string (e.g. ``"Q42"``).
        '''
        return f'{self.url}/w/rest.php/wikibase/v1/entities/items/{item}/aliases/en'

    def _build_item(self, identifier, label, description, statements = None):
        '''Build the payload dict for a new or existing Wikibase item.

        Args:
            identifier:  Existing Wikibase QID (empty string for new items).
            label:       English label string.
            description: English description string.
            statements:  Optional list of statement triples; defaults to ``[]``.

        Returns:
            Dict with keys ``id``, ``url``, ``label``, ``description``,
            and ``statements``.
        '''
        # Empty Statements if none provided
        if statements is None:
            statements = []
        # Build Item
        item = {'id': identifier,
                'url': self._items_url(),
                'label': label,
                'description':  description,
                'statements': statements}
        return item

    def _build_statement(self, identifier, content, data_type = "wikibase-item", qualifiers = None):
        '''Build the Wikibase REST API statement payload dict.

        Args:
            identifier:  Wikibase property ID string (e.g. ``"P31"``).
            content:     Statement value (QID, string, or typed literal).
            data_type:   Wikibase datatype string (default ``"wikibase-item"``).
            qualifiers:  Optional list of qualifier dicts; defaults to ``[]``.

        Returns:
            Dict in the shape expected by the Wikibase REST API
            ``POST .../statements`` endpoint.
        '''
        # Empty Qualifiers if none provided
        if qualifiers is None:
            qualifiers = []
        # Build Statement
        statement = {"statement":
                        {"property":
                            {"id": identifier,
                             "data_type": data_type},
                             "value":
                                {"type": "value",
                                 "content": content},
                             "qualifiers": qualifiers
                        }
                    }
        return statement

    def _build_alias(self, alias):
        '''Wrap *alias* in the ``{"aliases": …}`` payload dict expected by the API.

        Args:
            alias: List of alias strings.

        Returns:
            Dict ``{"aliases": alias}``.
        '''
        aliases_dict = {
          "aliases": alias
        }
        return aliases_dict

    def _normalize_aliases(self, aliases_dict: dict) -> list[str]:
        '''Convert a ``{index: alias}`` dict to a sorted, deduplicated list of strings.

        Args:
            aliases_dict: Dict mapping integer-like keys to alias strings.

        Returns:
            List of non-blank alias strings in ascending key order.
        '''
        return [
            a for _, a in sorted(aliases_dict.items())
            if isinstance(a, str) and a.strip()
        ]

    def build_relation_check_query(self):
        '''Build a SPARQL SELECT query that checks whether all RELATION entries already exist.

        Returns:
            SPARQL query string that selects one boolean variable per relation
            (``?RELATION0``, ``?RELATION1``, …).
        '''
        relation_keys = [k for k in self.state.dictionary if k.startswith('RELATION')]
        optional_blocks, bind_blocks = [], []

        for idx, key in enumerate(relation_keys):
            entry = self.state.dictionary[key]
            optional_block, bind_block = self._build_relation_block(idx, entry)
            if optional_block is None:
                continue
            optional_blocks.append(optional_block)
            bind_blocks.append(bind_block)

        query_body = '\n'.join(optional_blocks + bind_blocks)
        selectors = " ".join(f"?RELATION{idx}" for idx in range(len(relation_keys)))
        return f'\nSELECT {selectors} WHERE {{\n{query_body}\n}}'

    def _sparql_value(self, value, data_type):
        '''Format *value* as a SPARQL literal or IRI appropriate for *data_type*.

        Args:
            value:     Raw value string or QID.
            data_type: Wikibase datatype (``"wikibase-item"``, ``"string"``,
                       ``"quantity"``, ``"time"``, ``"monolingualtext"``,
                       or ``"math"``).

        Returns:
            SPARQL-formatted string (e.g. ``"wd:Q42"`` or ``"'text'"``).
        '''
        if data_type == 'wikibase-item':
            formatted_value = f'wd:{value}'
        elif data_type == 'string':
            escaped_value = value.replace("'", "\\'")
            formatted_value = f"'{escaped_value}'"
        elif data_type == 'quantity':
            formatted_value = f"'{value}'^^<http://www.w3.org/2001/XMLSchema#decimal>"
        elif data_type == 'time':
            formatted_value = f"'{value}'^^<http://www.w3.org/2001/XMLSchema#dateTime>"
        elif data_type == 'monolingualtext':
            escaped_value = value.replace("'", "\\'")
            formatted_value = f"'{escaped_value}'@en"
        elif data_type == 'math':
            escaped_value = value.replace("\\", "\\\\").replace("\"", "\\\"")
            formatted_value = f"'{escaped_value}'^^<http://www.w3.org/1998/Math/MathML>"
        else:
            formatted_value = f"'{value}'"
        return formatted_value

    def _build_qualifier_triples(self, qualifiers, idx):
        '''Build SPARQL triple patterns for a list of qualifier dicts.

        Args:
            qualifiers: List of qualifier dicts (each with ``property`` and
                        ``value`` sub-dicts).
            idx:        Statement index used to name the ``?statement<idx>``
                        SPARQL variable.

        Returns:
            SPARQL triple-pattern string (may be empty when *qualifiers* is empty).
        '''
        triples = ''
        for q in qualifiers:
            q_prop = q['property']['id']
            q_value = q['value']['content']
            q_data_type = q['property']['data_type']
            if q_value in self.state.dictionary and 'id' in self.state.dictionary[q_value]:
                q_value = self.state.dictionary[q_value]['id']
            triples += (
                f'    ?statement{idx} pq:{q_prop} '
                f'{self._sparql_value(q_value, q_data_type)} .\n'
            )
        return triples

    def _build_relation_block(self, idx, entry):
        '''Build the OPTIONAL and BIND SPARQL fragments for one RELATION entry.

        Args:
            idx:   Relation index used to name SPARQL variables.
            entry: RELATION payload dict from ``self.state.dictionary``.

        Returns:
            Tuple ``(optional_block, bind_block)`` strings, or ``(None, None)``
            when the target item is not yet in the dictionary.
        '''
        target_item_key = entry['url'].split('/')[-2]
        target_item_data = self.state.dictionary.get(target_item_key)
        if not target_item_data:
            return None, None

        target_item_id = target_item_data['id']
        statement = entry['payload']['statement']
        prop_id = statement['property']['id']
        value = statement['value']['content']
        data_type = statement['property']['data_type']

        if value in self.state.dictionary and 'id' in self.state.dictionary[value]:
            value = self.state.dictionary[value]['id']

        subject = f'wd:{target_item_id}'
        value_str = self._sparql_value(value, data_type)
        qualifiers = statement.get('qualifiers', [])
        qual_triples = self._build_qualifier_triples(qualifiers, idx)

        block = {
            'optional': (
                f'OPTIONAL {{\n'
                f'  {subject} p:{prop_id} ?statement{idx} .\n'
                f'  ?statement{idx} ps:{prop_id} {value_str} .\n'
                f'{qual_triples if qualifiers else ""}}}'
            ),
            'bind': f'BIND(BOUND(?statement{idx}) AS ?RELATION{idx})'
        }

        return block['optional'], block['bind']

    def _find_key_by_values(self, id_value, name_value, description_value):
        '''Look up the ``"Item<n>"`` key matching the given ID, Name, and Description.

        Args:
            id_value:          ``ID`` field value to match.
            name_value:        ``Name`` field value to match.
            description_value: ``Description`` field value to match.

        Returns:
            Matching ``"Item<n>"`` key string, or ``None`` if not found.
        '''
        for key, values in self.user_items.items():
            if (values['ID'] == id_value and
                values['Name'] == name_value and
                values['Description'] == description_value):
                return key
        return None

    def get_dictionary(self):
        '''Return the complete payload dictionary (items, relations, and aliases).

        The returned dict maps ``"Item<n>"``, ``"RELATION<n>"``, and
        ``"ALIAS<n>"`` keys to their respective payload entries.  This is the
        top-level structure posted to the Wikibase REST API by
        :class:`~MaRDMO.oauth2.OauthProviderMixin`.
        '''
        # Get Target Dictionary
        target_dictionary = self.state.dictionary
        return target_dictionary

    def get_item_key(self, value, role='subject'):
        """Look up the ``"Item<n>"`` key for *value* and optionally set it as the current subject.

        Args:
            value: Item dict with ``ID``, ``Name``, and ``Description`` fields.
            role:  ``'subject'`` (default) stores the item as the active
                   subject for subsequent :meth:`add_answer` calls;
                   ``'object'`` just returns the key without updating state.

        Returns:
            The ``"Item<n>"`` key string for *value*.

        Raises:
            ValueError: If *value* is empty or missing ``Name``/``Description``.
        """
        if not value:
            raise ValueError("Missing Item in Statement!")
        if not value.get('Name') or not value.get('Description'):
            raise ValueError("All Items need to have a 'Name' and 'Description'!")

        item_key = self._find_key_by_values(
            value['ID'],
            value['Name'],
            value['Description'],
        )

        if role == 'subject':
            self.state.subject = value
            self.state.subject_item = item_key

        return item_key

    def add_qualifier(self, identifier, data_type, content):
        '''Build a single-qualifier list for use in :meth:`add_answer`.

        Args:
            identifier: Wikibase property ID string for the qualifier (e.g. ``"P3"``).
            data_type:  Wikibase datatype string for the qualifier value.
            content:    Qualifier value (QID, string, or typed literal).

        Returns:
            Single-element list containing the qualifier dict.
        '''
        # Build Qualifer
        qualifier = [{"property":
                        {"id": identifier,
                         "data_type": data_type},
                         "value": 
                            {"type": "value",
                             "content": content}
                    }]
        return qualifier

    def add_data_properties(self, item_class):
        '''Add ``instance of`` statements for each data property selected on the current subject.

        Looks up the data-property URL → QID mapping for *item_class* and
        calls :meth:`add_answer` for every property value stored in
        ``subject["Properties"]``.

        Args:
            item_class: Entity class string passed to
                        ``self.wikibase["data_properties"]`` (e.g. ``"model"``).
        '''
        data_properties = self.wikibase['data_properties'](item_class)
        for prop in self.state.subject.get('Properties', {}).values():
            self.add_answer(
                verb=self.wikibase['properties']['instance of'],
                object_and_type=[
                    data_properties[prop],
                    'wikibase-item',
                ]
            )

    def add_check_results(self, check):
        '''Update each RELATION entry with its SPARQL existence check result.

        Args:
            check: List of SPARQL result binding dicts; the first element is
                   used (keyed by ``"RELATION<n>"``).
        '''
        relation_keys = [k for k in self.state.dictionary if k.startswith('RELATION')]
        for idx, key in enumerate(relation_keys):
            exists_key = f'RELATION{idx}'
            exists_value = check[0].get(exists_key, {}).get('value', 'false')
            self.state.dictionary[key]['exists'] = exists_value

    def check_math_relations_via_api(self, api_url):
        '''Check existence of math-datatype RELATION statements via wbgetentities.

        SPARQL returns math values as MathML, but portal stores LaTeX.  This
        method queries the Wikibase API directly to compare raw LaTeX values.

        Returns {relation_key: 'true'/'false'}.
        '''
        relation_keys = [k for k in self.state.dictionary if k.startswith('RELATION')]
        math_entries  = {}  # key → (item_qid, prop_id, latex, qualifiers)

        for key in relation_keys:
            entry     = self.state.dictionary[key]
            statement = entry['payload']['statement']
            if statement['property']['data_type'] != 'math':
                continue
            item_key = entry['url'].split('/')[-2]
            item_qid = self.state.dictionary.get(item_key, {}).get('id', '')
            if not item_qid:
                continue  # new item → statement cannot exist yet
            math_entries[key] = (
                item_qid,
                statement['property']['id'],
                statement['value']['content'],
                statement.get('qualifiers', []),
            )

        if not math_entries:
            return {}

        # Fetch claims for all relevant items
        items_needed   = set(v[0] for v in math_entries.values())
        claims_by_item = {}
        chunk_size     = 50

        for i in range(0, len(items_needed), chunk_size):
            chunk = list(items_needed)[i:i + chunk_size]
            try:
                resp = requests.get(
                    api_url,
                    params={
                        'action': 'wbgetentities',
                        'ids':    '|'.join(chunk),
                        'props':  'claims',
                        'format': 'json',
                    },
                    headers={'User-Agent': 'MaRDMO (https://zib.de; reidelbach@zib.de)'},
                    timeout=10,
                )
                resp.raise_for_status()
                for qid, entity in resp.json().get('entities', {}).items():
                    claims_by_item[qid] = entity.get('claims', {})
            except requests.exceptions.RequestException as exc:
                _logger.warning("Math relation API check failed: %s", exc)

        result = {}
        for key, (item_qid, prop_id, latex, qualifiers) in math_entries.items():
            exists = 'false'
            for claim in claims_by_item.get(item_qid, {}).get(prop_id, []):
                claim_val = claim.get('mainsnak', {}).get('datavalue', {}).get('value', '')
                if claim_val != latex:
                    continue
                if not qualifiers:
                    exists = 'true'
                    break
                # Check that all qualifiers match
                qual_match = True
                for q in qualifiers:
                    q_prop = q['property']['id']
                    q_val  = q['value']['content']
                    # Resolve temporary item key to actual QID if available
                    if q_val in self.state.dictionary:
                        q_val = self.state.dictionary[q_val].get('id', q_val)
                    api_qual_vals = {
                        c.get('datavalue', {}).get('value', {}).get('id')
                        for c in claim.get('qualifiers', {}).get(q_prop, [])
                    }
                    if q_val not in api_qual_vals:
                        qual_match = False
                        break
                if qual_match:
                    exists = 'true'
                    break
            result[key] = exists

        return result

    def add_aliases(self, aliases_dict):
        '''Add aliases for the current subject to the payload.

        For existing items (with a real QID), creates ``ALIAS`` entries for
        immediate posting.  For new items, stores the aliases on the pending
        item entry for batch creation.

        Args:
            aliases_dict: ``{index: alias_string}`` dict; does nothing when empty.
        '''
        if not aliases_dict:
            return
        aliases_list = self._normalize_aliases(aliases_dict)
        # Add Aliases
        if (
            self.state.dictionary[self.state.subject_item]['id']
        ):
            self._add_alias(
                item = self.state.subject_item,
                aliases = aliases_list
            )
        else:
            self._add_to_item_alias(
                item = self.state.subject_item,
                aliases = aliases_list
            )

    def add_answer(self, verb, object_and_type,
                   qualifier = None, subject = None):
        '''Add a single statement to the payload.

        For items that already exist on the portal (have a real QID), a
        ``RELATION`` entry is created.  For new items, the statement is
        appended to the item's ``statements`` list for batch creation.

        Args:
            verb:            Wikibase property ID string (e.g. ``"P31"``).
            object_and_type: Two-element list ``[value, datatype]`` where
                             *datatype* is a Wikibase type string such as
                             ``"wikibase-item"``, ``"string"``, or ``"math"``.
            qualifier:       Optional list of qualifier dicts built by
                             :meth:`add_qualifier`.
            subject:         ``"Item<n>"`` key of the subject item; defaults
                             to the current subject set by :meth:`get_item_key`.
        '''
        if subject is None:
            subject = self.state.subject_item
        if qualifier is None:
            qualifier = []
        # Gather Statement
        statement = {
            'property_id': verb,
            'datatype': object_and_type[1],
            'value': object_and_type[0]
        }
        # Pattern of New Item
        pattern = re.compile(r"^Item\d{10}$")
        # Add Relation
        if (
            self.state.dictionary[subject]['id']
        ):
            self._add_relation(
                item=subject,
                statement=statement,
                qualifier=qualifier
            )
        else:
            if (isinstance(statement['value'], str) and pattern.match(statement['value'])):
                self.dependency[subject].add(statement['value'])
            self._add_to_item_statement(
                item=subject,
                statement=statement,
                qualifier=qualifier
            )

    def add_answers(self, mardmo_property, wikibase_property, datatype = 'string'):
        '''Add one statement per entry in ``subject[mardmo_property]``.

        Iterates over all values stored under *mardmo_property* in the
        current subject dict and calls :meth:`add_answer` for each.

        Args:
            mardmo_property:  Key in the subject dict (e.g. ``"descriptionLong"``).
            wikibase_property: Wikibase property label looked up in
                               ``self.wikibase['properties']``.
            datatype:          Wikibase value datatype (default ``"string"``).
        '''
        for entry in self.state.subject.get(mardmo_property, {}).values():
            self.add_answer(
                verb=self.wikibase['properties'][wikibase_property],
                object_and_type=[
                    entry,
                    datatype,
                ]
            )

    def add_single_relation(
        self,
        statement,
        alt_statement = None,
        qualifier = None,
        reverse = False
    ):
        '''Add one statement per entry in ``subject[statement["relatant"]]``.

        If the relatant item exists in the payload dictionary, uses
        ``statement['relation']`` as the property; otherwise falls back to
        *alt_statement* with a string value.

        Args:
            statement:     Dict with ``relation`` (property ID) and
                           ``relatant`` (subject key) fields.
            alt_statement: Fallback dict used when the relatant is not in
                           the payload (optional).
            qualifier:     Pre-built qualifier list (optional).
            reverse:       If ``True``, the relatant becomes the subject and
                           the current item becomes the object.
        '''
        # Empty Qualifiers if none provided
        if qualifier is None:
            qualifier = []
        for entry in self.state.subject.get(statement['relatant'], {}).values():
            # Get Item Key
            entry_item = self.get_item_key(entry, 'object')
            if entry_item in self.state.dictionary:
                # Assign Object and Subject
                if reverse:
                    subject_item, object_item = entry_item, self.state.subject_item
                else:
                    subject_item, object_item = self.state.subject_item, entry_item
                # Add to Payload
                self.add_answer(
                    verb = statement['relation'],
                    object_and_type = [
                        object_item,
                        'wikibase-item',
                    ],
                    qualifier = qualifier,
                    subject = subject_item
                )
            else:
                # Add to Payload
                self.add_answer(
                    verb = alt_statement['relation'],
                    object_and_type = [
                        entry.get(alt_statement['relatant']),
                        'string',
                    ],
                    qualifier = qualifier
                )

    def add_multiple_relation(self, statement, optional_qualifier = None, reverse = False):
        '''Add one statement per (relation, relatant) pair in the current subject.

        Iterates over ``subject[statement["relation"]]`` and
        ``subject[statement["relatant"]]`` simultaneously, attaching optional
        series-ordinal, assumption, and object-role qualifiers as configured
        by *optional_qualifier*.

        Args:
            statement:          Dict with ``relation`` and ``relatant`` keys.
            optional_qualifier: List of qualifier type strings to attach; supported
                                values are ``"series ordinal"``, ``"assumes"``.
            reverse:            If ``True``, swap subject and object.
        '''

        if optional_qualifier is None:
            optional_qualifier = []

        for key, prop in self.state.subject.get(statement['relation'], {}).items():
            for key2 in self.state.subject.get(statement['relatant'], {}).get(key, {}):
                # Get Item Key
                relatant_item = self.get_item_key(
                    self.state.subject.get(statement['relatant'], {}).get(key, {}).get(key2, {}),
                    'object'
                )

                # Set Up Qualifier
                qualifier = []

                # Add Formulation and Task Order Numbers to Qualifier
                if 'series ordinal' in optional_qualifier:
                    for number in ('formulation_number', 'task_number'):
                        if self.state.subject.get(number, {}).get(key, {}):
                            qualifier = self.add_qualifier(
                                self.wikibase['properties']['series ordinal'],
                                'string', 
                                self.state.subject[number][key]
                            )

                # Add Assumptions to Qualifier
                if 'assumes' in optional_qualifier:
                    if self.state.subject.get('assumption', {}).get(key, {}):
                        for assumption in self.state.subject['assumption'][key].values():
                            assumption_item = self.get_item_key(
                                assumption,
                                'object'
                            )
                            qualifier.extend(
                                self.add_qualifier(
                                    self.wikibase['properties']['assumes'],
                                    'wikibase-item',
                                    assumption_item
                                )
                            )

                # Add Roles to Qualifier
                if len(self.wikibase['relations'][prop]) == 2:
                    if self.wikibase['relations'][prop][1] not in ('forward', 'backward'):
                        qualifier.extend(
                            self.add_qualifier(
                                self.wikibase['properties']['object has role'],
                                'wikibase-item',
                                self.wikibase['relations'][prop][1]
                            )
                        )

                # Assign Object and Subject
                if reverse or self.wikibase['relations'][prop][-1] == 'backward':
                    subject_item, object_item = relatant_item, self.state.subject_item
                else:
                    subject_item, object_item = self.state.subject_item, relatant_item

                # Add to Payload
                self.add_answer(
                    verb = self.wikibase['relations'][prop][0],
                    object_and_type = [
                        object_item,
                        'wikibase-item',
                    ],
                    qualifier = qualifier,
                    subject = subject_item
                )

    def add_in_defining_formula(self):
        '''Add ``in defining formula`` statements with ``symbol represents`` qualifiers.

        Iterates over ``subject["element"]`` entries, looks up each quantity
        item key, and adds a ``math``-typed statement linking the symbol LaTeX
        to the quantity item via a qualifier.
        '''
        for element in self.state.subject.get('element', {}).values():
            # Get Item Key
            quantity_item = self.get_item_key(
                element.get('quantity', {}),
                'object'
            )
            # Add Quantity Qualifier
            qualifier = self.add_qualifier(
                self.wikibase['properties']['symbol represents'],
                'wikibase-item',
                quantity_item
            )
            # Pattern of New Item
            pattern = re.compile(r"^Item\d{10}$")
            # Add Symbol to Payload
            if (
                self.state.dictionary[self.state.subject_item]['id']
                or self.state.subject_item == quantity_item
            ):
                self._add_relation(
                    item = self.state.subject_item,
                    statement = {
                        'property_id': self.wikibase['properties']['in defining formula'],
                        'value': element.get('symbol', ''),
                        'datatype': 'math'
                    },
                    qualifier = qualifier
                )
            else:
                if (isinstance(quantity_item, str) and pattern.match(quantity_item)):
                    self.dependency[self.state.subject_item].add(quantity_item)
                    self.add_answer(
                        verb=self.wikibase['properties']['in defining formula'],
                        object_and_type=[
                            element.get('symbol', ''),
                            'math',
                        ],
                        qualifier=qualifier
                    )

    def _add_entry(self, key, value):
        '''Insert *value* under *key* into ``self.state.dictionary``.

        Args:
            key:   Dict key (e.g. ``"Item0000000001"``).
            value: Payload entry dict to store.
        '''
        self.state.dictionary[key] = value

    def _add_to_item_alias(self, item, aliases):
        '''Store *aliases* list on the pending item entry for *item*.'''
        self.state.dictionary[item]['aliases'] = aliases

    def _add_to_item_statement(self, item, statement, qualifier=None):
        '''Append *statement* to the pending statement list of *item*.

        Used for new items that do not yet have a Wikibase QID; statements are
        batched and created together with the item.

        Args:
            item:       ``"Item<n>"`` key of the target item.
            statement:  Dict with ``property_id``, ``datatype``, and ``value``.
            qualifier:  Optional qualifier list (default ``[]``).
        '''
        if qualifier is None:
            qualifier = []
        self.state.dictionary[item]['statements'].append(
            [
                statement['property_id'],
                statement['datatype'],
                statement['value'],
                qualifier
            ]
        )

    def _add_relation(self, item, statement, qualifier=None):
        '''Create a ``RELATION<n>`` entry for a statement on an existing item.

        Args:
            item:       Wikibase QID or ``"Item<n>"`` key of the target item.
            statement:  Dict with ``property_id``, ``datatype``, and ``value``.
            qualifier:  Optional qualifier list (default ``[]``).
        '''
        if qualifier is None:
            qualifier = []
        key = f"RELATION{self.state.counter}"
        self.state.dictionary[key] = {
            'id': '',
            'url': self._statement_url(item),
            'payload': self._build_statement(
                statement['property_id'],
                statement['value'],
                statement['datatype'],
                qualifier
            )
        }
        self.state.counter += 1

    def _add_alias(self, item, aliases):
        '''Create one ``ALIAS<n>`` entry per alias for an existing item.

        Args:
            item:    Wikibase QID or ``"Item<n>"`` key of the target item.
            aliases: List of alias strings to register.
        '''
        for alias in aliases:
            key = f"ALIAS{self.state.counter}"
            self.state.dictionary[key] = {
                'id': '',
                'url': self._alias_url(item),
                'payload': self._build_alias(
                    alias = [alias]
                )
            }
            self.state.counter += 1

    def add_item_payload(self):
        '''Finalise the ``payload`` field for every pending ``Item*`` entry.

        Converts the accumulated ``statements`` list (raw ``[pid, dtype, value,
        qualifiers]`` tuples) into the Wikibase REST API item-creation format
        and stores it back in the dictionary under ``item_data["payload"]``.
        Must be called after all :meth:`add_answer` / :meth:`add_multiple_relation`
        calls and before posting.
        '''
        for item_id, item_data in self.state.dictionary.items():
            # Check if Item in Payload
            if not item_id.startswith('Item'):
                continue
            # Extract Information
            label = item_data.get("label", "")
            description = item_data.get("description", "")
            aliases = item_data.get("aliases", "")
            statements_input = item_data.get("statements", [])
            # Grouped statements by PID
            statements = {}
            for s in statements_input:
                pid, dtype, obj = s[0], s[1], s[2]
                qualifier = None
                if len(s) == 4:
                    qualifier = s[3]
                statement = {
                    "property": {"id": pid, "data_type": dtype},
                    "value": {"type": "value", "content": obj}
                }
                if qualifier:
                    statement["qualifiers"] = qualifier

                statements.setdefault(pid, []).append(statement)
            # Build payload
            payload = {
                "item": {
                    "labels": {"en": label},
                    "statements": statements
                }
            }
            if description:
                payload["item"]["descriptions"] = {"en": description}
            if aliases:
                payload["item"]["aliases"] = {"en": aliases}
            # Attach to original dict
            item_data["payload"] = payload

    def _check_mardi_and_raise(self, name: str, description: str):
        """Check if item exists in MaRDI Portal and raise error if it does."""
        mardi_identifier = query_item(name, description)
        if mardi_identifier:
            raise ValueError(
                f"An item ({mardi_identifier}) with the label '{name}' "
                f"and description '{description}' already exists on the MaRDI Portal. "
                "If you intend to use this item, please select it in the questionnaire. "
                "Otherwise, redefine it."
            )
        return mardi_identifier

    def _statement_by_id_type(self, value: dict, id_type: str):
        """Build the external-identifier statements for a user-defined item.

        Selects which identifier statements to add (Wikidata QID, ORCID iD,
        zbMath ID, or ISSN) based on *id_type* and the fields present in *value*.

        Args:
            value:   Item dict with optional keys ``ID``, ``orcid``, ``zbmath``,
                     and ``issn``.
            id_type: Source tag string (e.g. ``'wikidata'``,
                     ``'no author found'``, ``'no journal found'``).

        Returns:
            List of ``[property_id, datatype, value_str]`` statement triples.
        """
        statements = []
        if id_type == 'wikidata':
            # Add Wikidata ID
            statements.append(
                [
                    self.wikibase['properties']['Wikidata QID'],
                    'external-id',
                    value['ID'].split(':')[1]
                ]
            )
        if id_type == 'no author found':
            # Add ORCID ID Statement
            if value.get('orcid'):
                statements.append(
                    [
                        self.wikibase['properties']['ORCID iD'],
                        'external-id',
                        value['orcid']
                    ]
                )
            # Add zbMath ID Statement
            if value.get('zbmath'):
                statements.append(
                    [
                        self.wikibase['properties']['zbMATH author ID'],
                        'external-id',
                        value['zbmath']
                    ]
                )
            # If Authors has ID, add further Statements
            if statements:
                statements.append(
                    [
                        self.wikibase['properties']['instance of'],
                        'wikibase-item',
                        self.wikibase['items']['human']
                    ]
                )
                statements.append(
                    [
                        self.wikibase['properties']['MaRDI profile type'],
                        'wikibase-item',
                        self.wikibase['items']['MaRDI person profile']
                    ]
                )
        if id_type == 'no journal found':
            # Add ISSN ID Statement
            if value.get('issn'):
                statements.append(
                    [
                        self.wikibase['properties']['ISSN'],
                        'external-id',
                        value['issn']
                    ]
                )
            # Add further Statements
            statements.append(
                [
                    self.wikibase['properties']['instance of'],
                    'wikibase-item',
                    self.wikibase['items']['scientific journal']
                ]
            )
        return statements

    def process_items(self):
        """Populate the payload dictionary with an entry for every item in ``user_items``.

        Dispatches each item to a source-specific handler based on the prefix
        of its ``ID`` field (``mardi``, ``wikidata``, ``not found``,
        ``no author found``, ``no journal found``).  Existing MaRDI items are
        registered with their real QID; new items get an empty id and a
        seed list of statements.  Raises :exc:`ValueError` for Wikidata or
        user-created items whose label/description combination already exists
        on the MaRDI Portal.
        """
        handlers = {
            'mardi': lambda key, value: 
                self._add_entry(
                    key,
                    self._build_item(
                        value['ID'].split(':')[1],
                        value['Name'],
                        value['Description'],
                    )
                ),
            'wikidata': lambda key, value: (
                self._check_mardi_and_raise(
                    value['Name'],
                    value['Description']
                ),
                self._add_entry(
                    key,
                    self._build_item(
                        '',
                        value['Name'],
                        value['Description'],
                        self._statement_by_id_type(
                            value,
                            'wikidata'))
                )
            ),
            'not found': lambda key, value: (
                self._check_mardi_and_raise(
                    value['Name'],
                    value['Description']
                ),
                self._add_entry(
                    key,
                    self._build_item(
                        '',
                        value['Name'],
                        value['Description'],
                        self._statement_by_id_type(
                            value,
                            'not found'
                        )
                    )
                )
            ),
            'no author found': lambda key, value: (
                self._check_mardi_and_raise(
                    value['Name'],
                    value['Description']
                ),
                self._add_entry(
                    key,
                    self._build_item(
                        '',
                        value['Name'],
                        value['Description'],
                        self._statement_by_id_type(
                            value,
                            'no author found'
                        )
                    )
                )
            ),
            'no journal found': lambda key, value: (
                self._check_mardi_and_raise(
                    value['Name'],
                    value['Description']
                ),
                self._add_entry(
                    key,
                    self._build_item(
                        '',
                        value['Name'],
                        value['Description'],
                        self._statement_by_id_type(
                            value,
                            'no journal found'
                        )
                    )
                )
            ),
        }

        for key, value in self.user_items.items():
            if not value.get('ID'):
                continue
            for id_type, handler in handlers.items():
                if id_type in value['ID']:
                    if id_type == 'no author found':
                        if value['zbmath'] or value['orcid']:
                            handler(key, value)
                    else:
                        handler(key, value)
                    break
