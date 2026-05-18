'''Background worker for the cross-catalog MaRDI search questionnaire.

Dispatches on the selected search mode and builds a SPARQL query from the
user-supplied filter criteria, executes it against the MaRDI Portal, and
stores the results for the view layer to render.

Three search modes are supported:

- **InterdisciplinaryWorkflow** — filters: research objective, academic
  discipline, mathematical model, algorithm, software, hardware, method,
  instrument, data set.
- **MathematicalModel** — filters: model properties, research problem,
  academic discipline, computational task, formula, quantity.
- **Algorithm** — filters: algorithmic task, software.

Provides:

- ``search`` — entry point called by the view layer; mutates *answers* in
  place with ``"query"``, ``"no_results"``, and ``"links"`` keys.
'''

import html

from ..getters import get_item_url, get_items, get_properties, get_url
from ..queries import query_sparql
from .sparql import (
    QUERY_BASE_WORKFLOW_SEARCH,
    WF_RESEARCH_OBJ_SPARQL,
    WF_DISCIPLINE_SPARQL,
    WF_MODEL_SPARQL,
    WF_ALGORITHM_SPARQL,
    WF_SOFTWARE_SPARQL,
    WF_HARDWARE_SPARQL,
    WF_METHOD_SPARQL,
    WF_INSTRUMENT_SPARQL,
    WF_DATASET_SPARQL,
    QUERY_BASE_MODEL_SEARCH,
    MM_PROPERTY_TO_ITEM,
    MM_PROPERTY_SPARQL,
    MM_PROBLEM_SPARQL,
    MM_DISCIPLINE_SPARQL,
    MM_TASK_SPARQL,
    MM_FORMULA_SPARQL,
    MM_QUANTITY_SPARQL,
    QUERY_BASE_ALGORITHM_SEARCH,
    ALG_TASK_SPARQL,
    ALG_SOFTWARE_SPARQL,
)

def search(answers, options):
    '''Build SPARQL queries from user search criteria, execute them, and store results.

    Dispatches on ``answers["search"]["options"]`` to one of three search
    modes: Interdisciplinary Workflow, Mathematical Model, or Algorithm.
    For each mode, constructs a SPARQL query from the selected filter criteria,
    executes it against the appropriate endpoint (MaRDI Portal or MathAlgoDB),
    and writes the escaped query string, result count, and link list back into
    *answers*.

    Args:
        answers: Top-level answers dict (mutated in place with ``"query"``,
                 ``"no_results"``, and ``"links"`` keys).
        options: Global RDMO options dict used for option-value comparisons.

    Returns:
        The mutated *answers* dict.
    '''
    if answers['search'].get('options') == options['InterdisciplinaryWorkflow']:

        s = answers['search']
        items = get_items()
        props = get_properties()

        filter_keys = [
            'research-objective', 'academic-discipline', 'mathematical-model',
            'algorithm', 'software', 'hardware', 'method', 'instrument', 'data-set',
        ]
        if not any(s.get(k) for k in filter_keys):
            answers['query'] = 'Workflow search requested but no parameters defined.'
            answers['no_results'] = '0'
            answers['links'] = []
            return answers

        parts = []

        for idx, keyword in enumerate(s.get('research-objective', {}).values()):
            if keyword:
                parts.append(
                    f"  # research objective: {keyword}\n"
                    + WF_RESEARCH_OBJ_SPARQL.format(
                        idx=idx, keyword=keyword.lower(), **items, **props
                    )
                )

        for idx, item in enumerate(s.get('academic-discipline', {}).values()):
            qid = item['ID'].split(':')[1]
            parts.append(
                f"  # academic discipline: {item['Name']}\n"
                + WF_DISCIPLINE_SPARQL.format(idx=idx, qid=qid, **items, **props)
            )

        for idx, item in enumerate(s.get('mathematical-model', {}).values()):
            qid = item['ID'].split(':')[1]
            parts.append(
                f"  # mathematical model: {item['Name']}\n"
                + WF_MODEL_SPARQL.format(idx=idx, qid=qid, **items, **props)
            )

        for idx, item in enumerate(s.get('algorithm', {}).values()):
            qid = item['ID'].split(':')[1]
            parts.append(
                f"  # algorithm: {item['Name']}\n"
                + WF_ALGORITHM_SPARQL.format(idx=idx, qid=qid, **items, **props)
            )

        for idx, item in enumerate(s.get('software', {}).values()):
            qid = item['ID'].split(':')[1]
            parts.append(
                f"  # software: {item['Name']}\n"
                + WF_SOFTWARE_SPARQL.format(idx=idx, qid=qid, **items, **props)
            )

        for idx, item in enumerate(s.get('hardware', {}).values()):
            qid = item['ID'].split(':')[1]
            parts.append(
                f"  # hardware: {item['Name']}\n"
                + WF_HARDWARE_SPARQL.format(idx=idx, qid=qid, **items, **props)
            )

        for idx, item in enumerate(s.get('method', {}).values()):
            qid = item['ID'].split(':')[1]
            parts.append(
                f"  # method: {item['Name']}\n"
                + WF_METHOD_SPARQL.format(idx=idx, qid=qid, **items, **props)
            )

        for idx, item in enumerate(s.get('instrument', {}).values()):
            qid = item['ID'].split(':')[1]
            parts.append(
                f"  # instrument: {item['Name']}\n"
                + WF_INSTRUMENT_SPARQL.format(idx=idx, qid=qid, **items, **props)
            )

        for idx, item in enumerate(s.get('data-set', {}).values()):
            qid = item['ID'].split(':')[1]
            parts.append(
                f"  # data set: {item['Name']}\n"
                + WF_DATASET_SPARQL.format(idx=idx, qid=qid, **items, **props)
            )

        query = "\n".join(
            line
            for line in QUERY_BASE_WORKFLOW_SEARCH.format(
                "\n".join(parts),
                **items,
                **props,
            ).splitlines()
            if line.strip()
        )

        answers['query'] = html.escape(query).replace('\n', '<br>')

        results = query_sparql(query, get_url('mardi', 'sparql'))
        answers['no_results'] = str(len(results))

        links = []
        for result in results:
            links.append([
                result["label"]["value"],
                f"{get_item_url('mardi')}{result['qid']['value']}",
            ])
        answers['links'] = links

    elif answers['search'].get('options') == options['MathematicalModel']:

        s = answers['search']
        items = get_items()
        props = get_properties()

        filter_keys = [
            'mathematical-model-properties', 'research-problem',
            'academic-discipline', 'computational-task', 'formula', 'quantity',
        ]
        if not any(s.get(k) for k in filter_keys):
            answers['query'] = 'Model search requested but no parameters defined.'
            answers['no_results'] = '0'
            answers['links'] = []
            return answers

        parts = []

        for option_uri in s.get('mathematical-model-properties', {}).values():
            uri_tail = option_uri.rsplit('/', 1)[-1]
            item_key = MM_PROPERTY_TO_ITEM.get(uri_tail)
            if item_key:
                label = uri_tail.replace('-', ' ')
                parts.append(
                    f"  # model property: {label}\n"
                    + MM_PROPERTY_SPARQL.format(
                        qid=items[item_key], **items, **props
                    )
                )

        for idx, item in enumerate(s.get('research-problem', {}).values()):
            qid = item['ID'].split(':')[1]
            parts.append(
                f"  # research problem: {item['Name']}\n"
                + MM_PROBLEM_SPARQL.format(idx=idx, qid=qid, **items, **props)
            )

        for idx, item in enumerate(s.get('academic-discipline', {}).values()):
            qid = item['ID'].split(':')[1]
            parts.append(
                f"  # academic discipline: {item['Name']}\n"
                + MM_DISCIPLINE_SPARQL.format(idx=idx, qid=qid, **items, **props)
            )

        for idx, item in enumerate(s.get('computational-task', {}).values()):
            qid = item['ID'].split(':')[1]
            parts.append(
                f"  # computational task: {item['Name']}\n"
                + MM_TASK_SPARQL.format(idx=idx, qid=qid, **items, **props)
            )

        for idx, item in enumerate(s.get('formula', {}).values()):
            qid = item['ID'].split(':')[1]
            parts.append(
                f"  # formula: {item['Name']}\n"
                + MM_FORMULA_SPARQL.format(idx=idx, qid=qid, **items, **props)
            )

        for idx, item in enumerate(s.get('quantity', {}).values()):
            qid = item['ID'].split(':')[1]
            parts.append(
                f"  # quantity: {item['Name']}\n"
                + MM_QUANTITY_SPARQL.format(idx=idx, qid=qid, **items, **props)
            )

        query = "\n".join(
            line
            for line in QUERY_BASE_MODEL_SEARCH.format(
                "\n".join(parts),
                **items,
                **props,
            ).splitlines()
            if line.strip()
        )

        answers['query'] = html.escape(query).replace('\n', '<br>')

        results = query_sparql(query, get_url('mardi', 'sparql'))
        answers['no_results'] = str(len(results))

        links = []
        for result in results:
            links.append([
                result["label"]["value"],
                f"{get_item_url('mardi')}{result['qid']['value']}",
            ])
        answers['links'] = links

    elif answers['search'].get('options') == options['Algorithm']:

        s = answers['search']
        items = get_items()
        props = get_properties()

        filter_keys = ['algorithmic-task', 'software']
        if not any(s.get(k) for k in filter_keys):
            answers['query'] = (
                'Algorithm search requested but no parameters defined.'
            )
            answers['no_results'] = '0'
            answers['links'] = []
            return answers

        parts = []

        for idx, item in enumerate(s.get('algorithmic-task', {}).values()):
            qid = item['ID'].split(':')[1]
            parts.append(
                f"  # algorithmic task: {item['Name']}\n"
                + ALG_TASK_SPARQL.format(idx=idx, qid=qid, **items, **props)
            )

        for idx, item in enumerate(s.get('software', {}).values()):
            qid = item['ID'].split(':')[1]
            parts.append(
                f"  # software: {item['Name']}\n"
                + ALG_SOFTWARE_SPARQL.format(idx=idx, qid=qid, **items, **props)
            )

        query = "\n".join(
            line
            for line in QUERY_BASE_ALGORITHM_SEARCH.format(
                "\n".join(parts),
                **items,
                **props,
            ).splitlines()
            if line.strip()
        )

        answers['query'] = html.escape(query).replace('\n', '<br>')

        results = query_sparql(query, get_url('mardi', 'sparql'))
        answers['no_results'] = str(len(results))

        links = []
        for result in results:
            links.append([
                result["label"]["value"],
                f"{get_item_url('mardi')}{result['qid']['value']}",
            ])
        answers['links'] = links

    return answers
