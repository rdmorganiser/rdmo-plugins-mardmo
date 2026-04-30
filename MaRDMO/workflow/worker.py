'''Worker module for Interdisciplinary Workflow preview and export.

Provides :class:`prepareWorkflow`, which assembles RDMO questionnaire answers
into a :class:`~MaRDMO.payload.GeneratePayload` ready for submission to the
MaRDI Portal Wikibase instance.
'''

from .constants import preview_relations, REPRODUCIBILITY

from ..getters import (
    get_items,
    get_mathalgodb,
    get_mathmoddb,
    get_options,
    get_properties,
    get_url
)
from ..helpers import entity_relations, entity_relations_grouped, unique_items
from ..queries import query_sparql
from ..payload import GeneratePayload

class prepareWorkflow:
    '''Prepare interdisciplinary workflow answers for preview and export.

    Loads Wikibase vocabulary (items and properties) on instantiation so
    they are available to both :meth:`preview` and :meth:`export`.
    '''

    def __init__(self):
        '''Initialise with Wikibase items and properties from MaRDMOConfig.'''
        self.items = get_items()
        self.properties = get_properties()
        self.mathmoddb = get_mathmoddb()
        self.mathalgodb = get_mathalgodb()

    def preview(self, answers):
        '''Enrich the answers dict with derived display structures for the preview template.

        First iterates over :data:`~MaRDMO.workflow.constants.preview_relations` and calls
        :func:`~MaRDMO.helpers.entity_relations` for each entry to resolve cross-entity
        relation labels (e.g. Workflow → Process Step) into the ``answers`` dict — the same
        pattern used by the model and algorithm preview workers.

        Then builds ``model_task_pairs`` — an ordered list of dicts with keys ``model``,
        ``tasks``, ``has_model``, and ``has_tasks`` — for every workflow in the project
        and stores it directly on each workflow's sub-dict
        (``answers['workflow'][i]['model_task_pairs']``) so the template can access it as
        ``values.model_task_pairs`` inside the ``{% for values in answers.workflow.values %}``
        loop without integer-key lookups.  Indices from both models *and* tasks are unioned
        so that a task with no matching model (or vice versa) still produces a row with the
        appropriate validation flags set.

        Similarly builds ``algorithm_software_pairs`` and ``method_instrument_pairs`` —
        ordered lists of dicts with generic keys ``primary``, ``qualifier``,
        ``has_primary``, and ``has_qualifier`` — for every process step.  Index *i*
        pairs algorithm *i* with software *i* (and method *i* with instrument *i*);
        a missing partner raises a validation flag rendered as a red warning via the
        ``_relation_block_single_with_qualifier.html`` include.

        Args:
            answers: Top-level answers dict produced by ``get_post_data``.

        Returns:
            The same *answers* dict with relation labels and ``model_task_pairs`` added.
        '''

        # Prepare Relations for Preview
        for relation in preview_relations:
            fn = entity_relations_grouped if relation.get('grouped') else entity_relations
            fn(
                data = answers,
                idx = {
                    'from': relation['from_idx'],
                    'to': relation['to_idx']
                },
                entity = {
                    'relation': relation['relation'],
                    'old_name': relation['old_name'],
                    'new_name': relation['new_name'],
                    'encryption': relation['encryption']
                },
                order = {
                    'formulation': relation['formulation'],
                    'task': relation['task']
                },
                assumption = relation['assumption'],
                mapping = self.mathmoddb
            )

        for wf_data in answers.get('workflow', {}).values():
            models = wf_data.get('model', {})
            tasks  = wf_data.get('task', {})
            all_indices = sorted(set(models) | set(tasks))
            wf_data['model_task_pairs'] = [
                {
                    'model':     models.get(idx),
                    'tasks':     list(tasks.get(idx, {}).values()),
                    'has_model': bool(models.get(idx)),
                    'has_tasks': bool(tasks.get(idx)),
                }
                for idx in all_indices
            ]
        print(answers)
        for ps_data in answers.get('processstep', {}).values():
            # RelationA keys are 'set_index|collection_index' strings;
            # group all algorithms sharing the same set_index into one list.
            algo_by_set = {}
            for key, val in ps_data.get('RelationA', {}).items():
                set_idx = int(str(key).split('|')[0])
                algo_by_set.setdefault(set_idx, []).append(val)
            software = ps_data.get('RelationS', {})
            hardware = ps_data.get('RelationH', {})
            software_doc = ps_data.get('software-documentation', {})
            algo_params = ps_data.get('algorithm-parameter', {})
            all_indices = sorted(set(algo_by_set) | set(software) | set(hardware) | set(software_doc))
            ps_data['algorithm_software_pairs'] = [
                {
                    'primary':       algo_by_set.get(idx, []),
                    'qualifier':     software.get(idx),
                    'has_primary':   bool(algo_by_set.get(idx)),
                    'has_qualifier': bool(software.get(idx)),
                    'parameters':    ', '.join(
                        v[1][1] for v in sorted(algo_params.get(idx, {}).items())
                        if v[1][1]
                    ),
                    'software_doc':  software_doc.get(idx),
                    'hardware':      hardware.get(idx),
                }
                for idx in all_indices
            ]

            # Use raw MRelatant/IRelatant dicts so the template can display
            # Name (Description) for inline items that have no dedicated section.
            meth_by_set = {
                set_idx: [raw]
                for set_idx, raw in ps_data.get('MRelatant', {}).items()
            }
            instruments = ps_data.get('IRelatant', {})
            method_doc  = ps_data.get('method-documentation', {})
            meth_params = ps_data.get('method-parameter', {})
            all_indices = sorted(set(meth_by_set) | set(instruments) | set(method_doc))
            ps_data['method_instrument_pairs'] = [
                {
                    'primary':       meth_by_set.get(idx, []),
                    'qualifier':     instruments.get(idx),
                    'has_primary':   bool(meth_by_set.get(idx)),
                    'has_qualifier': bool(instruments.get(idx)),
                    'parameters':    ', '.join(
                        v[1][1] for v in sorted(meth_params.get(idx, {}).items())
                        if v[1][1]
                    ),
                    'method_doc':    method_doc.get(idx),
                }
                for idx in all_indices
            ]

        return answers

    def export(self, data, title, url):
        '''Assemble and return the complete Wikibase payload for a Workflow documentation export.

        Args:
            data:  Top-level workflow answers dict produced by ``get_post_data``.
            title: Workflow title string used to seed item labels.
            url:   Target Wikibase API URL for the upload.

        Returns:
            Tuple ``(payload_dict, dependency_order)`` ready for
            :meth:`~MaRDMO.oauth2.OauthProviderMixin.post`.
        '''
        
        items, dependency = unique_items(data, title)
        for key, value in items.items():
            print(key, value)
        payload = GeneratePayload(
            dependency = dependency,
            user_items = items,
            url = url,
            wikibase = {
                'items': get_items(),
                'properties': get_properties(),
            }
        )

        # Load Options
        options = get_options()

        # Add / Retrieve Components of Interdisciplinary Workflow Item
        payload.process_items()

        ### Add additional Software Information
        for software in data.get('software', {}).values():

            # Continue if no ID exists
            if not software.get('ID'):
                continue

            # Get Item Key
            payload.get_item_key(software)

            # Add Class
            payload.add_answer(
                    verb=self.properties['instance of'],
                    object_and_type=[
                        self.items['software'],
                        'wikibase-item',
                    ]
                )

            # Add References of the Software
            for reference in software.get('Reference', {}).values():
                if reference[0] == options['DOI']:
                    payload.add_answer(
                        verb=self.properties['DOI'],
                        object_and_type=[
                            reference[1],
                            'external-id',
                        ]
                    )
                elif reference[0] == options['SWMATH']:
                    payload.add_answer(
                        verb=self.properties['swMath work ID'],
                        object_and_type=[
                            reference[1],
                            'external-id',
                        ]
                    )
                elif reference[0] == options['SOURCECODE_URL']:
                    payload.add_answer(
                        verb=self.properties['source code reposiory URL'],
                        object_and_type=[
                            reference[1],
                            'url',
                        ]
                    )
                elif reference[0] == options['DESCRIPTION_URL']:
                    payload.add_answer(
                        verb=self.properties['described at URL'],
                        object_and_type=[
                            reference[1],
                            'url',
                        ]
                    )

            # Add Programming Languages
            payload.add_single_relation(
                statement = {
                    'relation': self.properties['programmed in'],
                    'relatant': 'programminglanguage'
                }
            )

            # Add Dependencies
            payload.add_single_relation(
                statement = {
                    'relation': self.properties['depends on software'],
                    'relatant': 'dependency'
                }
            )

            # Add Source Code Repository
            if software.get('Published', [''])[0] == options['YesText']:
                payload.add_answer(
                    verb=self.properties['source code repository URL'],
                    object_and_type=[
                        software['Published'][1],
                        'url',
                    ]
                )

            # Add Documentation / Manual
            if software.get('Documented', [''])[0] == options['YesText']:
                payload.add_answer(
                    verb=self.properties['user manual URL'],
                    object_and_type=[
                        software['Documented'][1],
                        'url',
                    ]
                )

        ### Add additional Hardware Information
        for hardware in data.get('hardware', {}).values():

            # Continue if no ID exists
            if not hardware.get('ID'):
                continue

            # Get Item Key
            payload.get_item_key(hardware)

            # Add Class
            payload.add_answer(
                verb=self.properties['instance of'],
                object_and_type=[
                    self.items['computer hardware'],
                    'wikibase-item',
                ]
            )

            # Add CPU
            payload.add_single_relation(
                statement = {
                    'relation': self.properties['CPU'],
                    'relatant': 'cpu'
                }
            )

            # Add Number of Computing Nodes
            if hardware['Nodes']:
                payload.add_answer(
                    verb=self.properties['has part(s)'],
                    object_and_type=[
                        self.items['compute node'],
                        'wikibase-item',
                    ],
                    qualifier = [
                                    {
                                        "property": {
                                            "id": self.properties['quantity_property'],
                                        },
                                        "value": {
                                            "type": "value",
                                            "content": {
                                                "amount": f"+{hardware['Nodes']}",
                                                "unit": "1",
                                            },
                                        },
                                    }
                                ]
                )

            # Add Number of Processor Cores
            if hardware['Cores']:
                payload.add_answer(
                    verb=self.properties['number of processor cores'],
                    object_and_type=[
                        {
                            "amount": f"+{hardware['Cores']}",
                            "unit":"1"
                        },
                        'quantity'
                    ]
                )

        ### Add additional Dataset Information
        for dataset in data.get('dataset', {}).values():

            # Continue if no ID exists
            if not dataset.get('ID'):
                continue

            # Get Item Key
            payload.get_item_key(dataset)

            # Add Class
            payload.add_answer(
                verb=self.properties['instance of'],
                object_and_type=[
                    self.items['data set'],
                    'wikibase-item',
                ]
            )

            # Size of the data set
            if dataset.get('Size'):
                if dataset['Size'][0] == options['kilobyte']:
                    verb = self.properties['data size']
                    object = {
                        "amount": f"+{dataset['Size'][1]}",
                        "unit": f"{get_url('mardi', 'uri')}/entity/{self.items['kilobyte']}"
                    }
                elif dataset['Size'][0] == options['megabyte']:
                    verb = self.properties['data size']
                    object = {
                        "amount": f"+{dataset['Size'][1]}",
                        "unit": f"{get_url('mardi', 'uri')}/entity/{self.items['megabyte']}"
                    }
                elif dataset['Size'][0] == options['gigabyte']:
                    verb = self.properties['data size']
                    object = {
                        "amount": f"+{dataset['Size'][1]}",
                        "unit": f"{get_url('mardi', 'uri')}/entity/{self.items['gigabyte']}"
                    }
                elif dataset['Size'][0] == options['terabyte']:
                    verb = self.properties['data size']
                    object = {
                        "amount": f"+{dataset['Size'][1]}",
                        "unit": f"{get_url('mardi', 'uri')}/entity/{self.items['terabyte']}"
                    }
                elif dataset['Size'][0] == options['items']:
                    verb = self.properties['number of records']
                    object = {
                        "amount": f"+{dataset['Size'][1]}","unit":"1"
                    }

                payload.add_answer(
                    verb=verb,
                    object_and_type=[
                        object,
                        'quantity',
                    ]
                )

            # Add File Format
            if dataset.get('FileFormat'):
                payload.add_answer(
                    verb=self.properties['file extension'],
                    object_and_type=[
                        dataset['FileFormat'],
                        'string',
                    ]
                )

            # Add binary or text data
            if dataset.get('BinaryText'):
                if dataset['BinaryText'] == options['binary']:
                    payload.add_answer(
                        verb=self.properties['instance of'],
                        object_and_type=[
                            self.items['binary data'],
                            'wikibase-item',
                        ]
                    )
                elif dataset['BinaryText'] == options['text']:
                    payload.add_answer(
                        verb=self.properties['instance of'],
                        object_and_type=[
                            self.items['text data'],
                            'wikibase-item',
                        ]
                    )

            # Data Set Proprietary
            if dataset.get('Proprietary'):
                if dataset['Proprietary'] == options['Yes']:
                    payload.add_answer(
                        verb=self.properties['instance of'],
                        object_and_type=[
                            self.items['proprietary information'],
                            'wikibase-item',
                        ]
                    )
                elif dataset['Proprietary'] == options['No']:
                    payload.add_answer(
                        verb=self.properties['instance of'],
                        object_and_type=[
                            self.items['open data'],
                            'wikibase-item',
                        ]
                    )

            # Data Set to Publish
            if dataset.get('ToPublish'):
                if dataset['ToPublish'].get(0, ['',''])[0] == options['Yes']:
                    payload.add_answer(
                        verb=self.properties['mandates'],
                        object_and_type=[
                            self.items['data publishing'],
                            'wikibase-item',
                        ]
                    )
                    if dataset['ToPublish'].get(1, ['',''])[0] == options['DOI']:
                        payload.add_answer(
                            verb=self.properties['DOI'],
                            object_and_type=[
                                dataset['ToPublish'][1][1],
                                'external-id',
                            ]
                        )
                    if dataset['ToPublish'].get(2, ['',''])[0] == options['URL']:
                        payload.add_answer(
                            verb=self.properties['URL'],
                            object_and_type=[
                                dataset['ToPublish'][2][2],
                                'url',
                            ]
                        )

            # Data Set To Archive
            if dataset.get('ToArchive'):
                if dataset['ToArchive'][0] == options['YesText']:
                    qualifier = []
                    if dataset['ToArchive'][1]:
                        qualifier = payload.add_qualifier(
                            self.properties['end time'],
                            'time',
                            {
                                "time": f"+{dataset['ToArchive'][1]}-00-00T00:00:00Z",
                                "precision": 9,
                                "calendarmodel": "http://www.wikidata.org/entity/Q1985727"
                            }
                        )
                    payload.add_answer(
                            verb=self.properties['mandates'],
                            object_and_type=[
                                self.items['research data archiving'],
                                'wikibase-item',
                            ],
                            qualifier=qualifier
                        )

        ### Add Process Step Information
        for processstep in data.get('processstep', {}).values():

            # Continue if no ID exists
            if not processstep.get('ID'):
                continue

            # Get Item Key
            payload.get_item_key(processstep)

            # Add Class
            payload.add_answer(
                verb=self.properties['instance of'],
                object_and_type=[
                    self.items['process step'],
                    'wikibase-item',
                ]
            )

            # Add Input Data Sets
            payload.add_single_relation(
                statement = {
                    'relation': self.properties['input data set'],
                    'relatant': 'input'
                }
            )

            # Add Output Data Sets
            payload.add_single_relation(
                statement = {
                    'relation': self.properties['output data set'],
                    'relatant': 'output'
                }
            )

            # Add applied Methods
            for method in processstep.get('method', {}).values():
                # Continue if no ID exists
                if not method.get('ID'):
                    continue
                # Get Entry Key
                method_item = payload.get_item_key(method, 'object')
                # Get Qualifier
                qualifier = []
                for parameter in method.get('Parameter', {}).values():
                    qualifier.extend(
                        payload.add_qualifier(
                            self.properties['comment'],
                            'string',
                            parameter
                        )
                    )
                # Add to Payload
                payload.add_answer(
                            verb=self.properties['uses'],
                            object_and_type=[
                                method_item,
                                'wikibase-item',
                            ],
                            qualifier=qualifier
                        )

            # Add Software Environment
            payload.add_single_relation(
                statement = {
                    'relation': self.properties['platform'], 
                    'relatant': 'environmentSoftware'
                },
                qualifier = payload.add_qualifier(
                    self.properties['object has role'],
                    'wikibase-item',
                    self.items['software']
                )
            )

            # Add Instrument Environment
            payload.add_single_relation(
                statement = {
                    'relation': self.properties['platform'], 
                    'relatant': 'environmentInstrument'
                },
                qualifier = payload.add_qualifier(
                    self.properties['object has role'],
                    'wikibase-item',
                    self.items['research tool']
                )
            )

            # Add Disciplines (math and non-math)
            for discipline in processstep.get('discipline', {}).values():
                # Check if new ID exists
                if 'msc:' in discipline.get('ID'):
                    _, id = discipline['ID'].split(':')
                    payload.add_answer(
                        verb=self.properties['MSC ID'],
                        object_and_type=[
                            id,
                            'external-id',
                        ]
                    )
                else:
                    # Get Discipline Key
                    discipline_item = payload.get_item_key(discipline, 'object')
                    # Add to Payload
                    payload.add_answer(
                        verb=self.properties['field of work'],
                        object_and_type=[
                            discipline_item,
                            'wikibase-item',
                        ]
                    )

        for publication in data.get('publication', {}).values():

            # Continue if no ID exists
            if not publication.get('ID'):
                continue

            # Get Item Key
            payload.get_item_key(publication)

            if 'mardi' not in publication['ID']:

                # Set and add the Class of the Publication
                if publication.get('entrytype') == 'scholarly article':
                    pclass = self.items['scholarly article']
                else:
                    pclass = self.items['publication']

                payload.add_answer(
                    verb=self.properties['instance of'],
                    object_and_type=[
                        pclass,
                        'wikibase-item',
                    ]
                )

                # Add Publication Profile
                payload.add_answer(
                        verb = self.properties["MaRDI profile type"],
                        object_and_type = [
                            self.items["MaRDI publication profile"],
                            "wikibase-item"
                        ],
                    )

                # Add the DOI of the Publication
                if publication.get('reference', {}).get(0):
                    payload.add_answer(
                        verb=self.properties['DOI'],
                        object_and_type=[
                            publication['reference'][0][1],
                            'external-id',
                        ]
                    )

                # Add the Title of the Publication
                if publication.get('title'):
                    payload.add_answer(
                        verb=self.properties['title'],
                        object_and_type=[
                            {"text": publication['title'], "language": "en"},
                            'monolingualtext',
                        ]
                    )

                # Add the Volume of the Publication
                if publication.get('volume'):
                    payload.add_answer(
                        verb=self.properties['volume'],
                        object_and_type=[
                            publication['volume'],
                            'string',
                        ]
                    )

                # Add the Issue of the Publication
                if publication.get('issue'):
                    payload.add_answer(
                        verb=self.properties['issue'],
                        object_and_type=[
                            publication['issue'],
                            'string',
                        ]
                    )

                # Add the Page(s) of the Publication
                if publication.get('page'):
                    payload.add_answer(
                        verb=self.properties['page(s)'],
                        object_and_type=[
                            publication['page'],
                            'string',
                        ]
                    )

                # Add the Date of the Publication
                if publication.get('date'):
                    payload.add_answer(
                        verb=self.properties['publication date'],
                        object_and_type=[
                            {
                                "time": f"+{publication['date']}T00:00:00Z",
                                "precision": 11,
                                "calendarmodel": "http://www.wikidata.org/entity/Q1985727"
                            },
                            'time',
                        ]
                    )

                # Add the Language of the Publication
                payload.add_single_relation(
                    statement = {
                        'relation': self.properties['language of work or name'],
                        'relatant': 'language'
                    }
                )

                # Add the Journal of the Publication
                payload.add_single_relation(
                    statement = {
                        'relation': self.properties['published in'],
                        'relatant': 'journal'
                    }
                )

                # Add the Authors of the Publication
                payload.add_single_relation(
                    statement = {
                        'relation': self.properties['author'],
                        'relatant': 'author'
                    },
                    alt_statement = {
                        'relation': self.properties['author name string'], 
                        'relatant': 'Name'
                    }
                )

        # Add Interdisciplinary Workflow Information
        workflow = {
            'ID': 'not found',
            'Name': title,
            'Description': data.get('workflow', {}).get('objective')
        }

        # Get Item Key
        payload.get_item_key(workflow)

        # Add Class
        payload.add_answer(
            verb=self.properties['instance of'],
            object_and_type=[
                self.items['research workflow'],
                'wikibase-item',
            ]
        )

        # Procedure Description to Workflow
        if data.get('workflow', {}).get('descriptionLong'):
            payload.add_answer(
                verb=self.properties['description'],
                object_and_type=[
                    data['workflow']['descriptionLong'],
                    'string',
                ]
            )

        # Add Reproducibility Aspects
        for key, value in REPRODUCIBILITY.items():
            if data.get('reproducibility', {}).get(key) == options['Yes']:
                qualifier = []
                if data['reproducibility'].get(f'{key}condition'):
                    qualifier.extend(
                        payload.add_qualifier(
                            self.properties['comment'],
                            'string',
                            data['reproducibility'][f'{key}condition']
                        )
                    )
                payload.add_answer(
                    verb=self.properties['instance of'],
                    object_and_type=[
                        self.items[value],
                        'wikibase-item',
                    ],
                    qualifier=qualifier
                )

        # Add Transferability Aspects
        if data.get('reproducibility', {}).get('transferability'):
            qualifier = []
            for value in data['reproducibility']['transferability'].values():
                qualifier.extend(
                    payload.add_qualifier(
                        self.properties['comment'],
                        'string',
                        value
                    )
                )
            payload.add_answer(
                verb=self.properties['instance of'],
                object_and_type=[
                    self.items['transferable research workflow'],
                    'wikibase-item',
                ],
                qualifier=qualifier
            )

        # Add Model and Task the Workflow Uses
        if data.get('model'):
            #Continue if ID exists
            if data['model'].get('ID'):
                # Get Item Key
                model_item = payload.get_item_key(data['model'], 'object')
                # Add Statement with Qualifier
                qualifier = []
                for task in data['model'].get('task', {}).values():
                    qualifier.extend(
                        payload.add_qualifier(
                            self.properties['used by'],
                            'wikibase-item',
                            payload.get_item_key(task, 'object')
                        )
                    )
                payload.add_answer(
                    verb=self.properties['uses'],
                    object_and_type=[
                        model_item,
                        'wikibase-item',
                    ],
                    qualifier=qualifier
                )

        # Add Software the Workflow uses
        for value in data.get('software', {}).values():
            # Continue if no ID exists
            if not value.get('ID'):
                continue
            # Get Item Key
            software_item = payload.get_item_key(value, 'object')
            # Add Statement with Qualifier
            qualifier = []
            for hardware in data.get('hardware', {}).values():
                for software in hardware.get('software', {}).values():
                    if (software.get('ID'), software.get('Name'), software.get('Description')) == (value['ID'], value['Name'], value['Description']):
                        hardware_item = payload.get_item_key(hardware, 'object')
                        qualifier.extend(payload.add_qualifier(self.properties['platform'], 'wikibase-item', hardware_item))
            if value.get('Version'):
                qualifier = payload.add_qualifier(
                    self.properties['software version identifier'],
                    'string',
                    value['Version']
                )
            payload.add_answer(
                verb=self.properties['uses'],
                object_and_type=[
                    software_item,
                    'wikibase-item',
                ],
                qualifier=qualifier
            )

        # Add Hardware the Workflow Uses
        for value in data.get('hardware', {}).values():
            # Continue if no ID exists
            if not value.get('ID'):
                continue
            # Get Item Key
            hardware_item = payload.get_item_key(value, 'object')
            # Add Satement with Qualifier
            qualifier = []
            for compiler in value.get('compiler', {}).values():
                qualifier.extend(
                    payload.add_qualifier(
                        self.properties['uses'],
                        'wikibase-item',
                        payload.get_item_key(compiler, 'object')
                    )
                )
            payload.add_answer(
                verb=self.properties['uses'],
                object_and_type=[
                    hardware_item,
                    'wikibase-item',
                ],
                qualifier=qualifier
            )

        # Add Data Sets the Workflow Uses
        for value in data.get('dataset', {}).values():
            # Continue if no ID exists
            if not value.get('ID'):
                continue
            # Get Item Key
            dataset_item = payload.get_item_key(value, 'object')
            # Add Statement
            payload.add_answer(
                verb=self.properties['uses'],
                object_and_type=[
                    dataset_item,
                    'wikibase-item',
                ]
            )

        # Add Process Steps the Workflow Uses
        for value in data.get('processstep', {}).values():
            # Continue if no ID exists
            if not value.get('ID'):
                continue
            # Get Item Key
            processstep_item = payload.get_item_key(value, 'object')
            # Add Statement with Qualifier
            qualifier = []
            for parameter in value.get('parameter', {}).values():
                qualifier.extend(
                    payload.add_qualifier(
                        self.properties['comment'],
                        'string',
                        parameter
                    )
                )
            payload.add_answer(
                verb=self.properties['uses'],
                object_and_type=[
                    processstep_item,
                    'wikibase-item',
                ],
                qualifier=qualifier
            )

        # Add Publications related to the Workflow
        for value in data.get('publication', {}).values():
            # Continue if no ID exists
            if not value.get('ID'):
                continue
            # Get Item Key
            publication_item = payload.get_item_key(value, 'object')
            # Add Statement
            payload.add_answer(
                verb=self.properties['cites work'],
                object_and_type=[
                    publication_item,
                    'wikibase-item',
                ]
            )

        # Construct Item Payloads
        payload.add_item_payload()

        # If Relations are added, check if they exist
        if any(key.startswith('RELATION') for key in payload.get_dictionary()):

            # Generate SPARQL Check Query
            query = payload.build_relation_check_query()

            # Perform Check Query for Relations
            check = query_sparql(query, get_url('mardi', 'sparql'))

            # Add Check Results
            payload.add_check_results(check)

        return payload.get_dictionary(), payload.dependency
