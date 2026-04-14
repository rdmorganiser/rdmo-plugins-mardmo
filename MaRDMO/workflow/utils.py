'''Utility functions for extracting and normalising workflow-related data.

Provides helpers that read structured answers from the RDMO questionnaire and
derive derived values (discipline labels, data-set sizes, references, archive
URLs) needed by the workflow worker and handler layers.

Provides:

- ``get_discipline`` — derive the research discipline label from questionnaire answers
- ``get_size``       — extract the data-set size value from answer options
- ``get_reference``  — extract a data-set or instrument reference identifier
- ``get_archive``    — extract the data-archive URL or identifier
'''

from .constants import data_set_reference_ids

def get_discipline(answers):
    '''Partition process-step disciplines into non-math and MSC (math subject classification) categories.

    Iterates over all ``processstep`` discipline entries in *answers*, deduplicates
    them by ID, and adds two new top-level keys to *answers*:

    * ``nonmathdiscipline`` – items with a ``mardi:`` or ``wikidata:`` prefix
    * ``mathsubject``       – items with an ``msc:`` prefix

    Args:
        answers: Top-level answers dict (mutated in place).

    Returns:
        The mutated *answers* dict.
    '''
    ids = []
    md = 0
    nmd = 0
    for key in answers.get('processstep', []):
        for key2 in answers['processstep'][key].get('discipline', []):
            if not answers['processstep'][key]['discipline'][key2].get('ID'):
                continue
            if answers['processstep'][key]['discipline'][key2]['ID'] in ids:
                continue
            if answers['processstep'][key]['discipline'][key2]['ID'].split(':')[0] in ('mardi', 'wikidata'):
                answers.setdefault('nonmathdiscipline', {}).update(
                    {
                        nmd:
                            {
                                'ID': answers['processstep'][key]['discipline'][key2]['ID'],
                                'Name': answers['processstep'][key]['discipline'][key2]['Name']
                            }
                    }
                )
                nmd += 1
                ids.append(answers['processstep'][key]['discipline'][key2]['ID'])
            elif answers['processstep'][key]['discipline'][key2]['ID'].split(':')[0] == 'msc':
                answers.setdefault('mathsubject', {}).update(
                    {
                        md:
                            {
                                'ID': answers['processstep'][key]['discipline'][key2]['ID'],
                                'Name': answers['processstep'][key]['discipline'][key2]['Name']
                            }
                    }
                )
                md += 1
                ids.append(answers['processstep'][key]['discipline'][key2]['ID'])
    return answers

def get_size(data, options):
    '''Extract the size unit and value from a data-set answer dict.

    Resolves the unit from either ``size_unit`` (RDMO option URI) or falls
    back to ``items`` when a record count is given.

    Args:
        data:    Answer sub-dict for the data-set size questions.
        options: Options dict mapping RDMO option URIs to string values.

    Returns:
        ``[unit, value]`` if both are present; ``[]`` otherwise.
    '''
    size_unit = data.get('size_unit', {}).get('value', '')
    size_value = data.get('size_value', {}).get('value', '')
    size_record = data.get('size_record', {}).get('value', '')

    unit = options.get(size_unit) if size_unit else (options['items'] if size_record else '')
    value = size_value or size_record

    return [unit, value] if unit and value else []

def get_reference(data, options):
    '''Build the reference dict for a data-set answer dict.

    Iterates over the predefined ``data_set_reference_ids`` keys and maps
    each present value to ``[option_uri, value]`` at a numeric index.

    Args:
        data:    Answer sub-dict for the data-set reference questions.
        options: Options dict mapping RDMO option URIs to string values.

    Returns:
        Dict ``{index: [option_uri, value]}`` for all present references;
        empty dict if none are set.
    '''
    result = {}

    for idx, key in enumerate(data_set_reference_ids):
        if key in ('Yes', 'No'):
            if value := data.get('publish', {}).get('value') == key:
                result[idx] = [options[key], '']
        else:
            if value := data.get(key, {}).get('value'):
                result[idx] = [options[key], value]

    return result

def get_archive(data, options):
    '''Extract archival intent and optional end-year from a data-set answer dict.

    Args:
        data:    Answer sub-dict for the data-set archival questions.
        options: Options dict mapping RDMO option URIs to string values.

    Returns:
        ``[archive_option, year]`` if archival is set; ``[]`` otherwise.
        *year* is the first four characters of the ``end_time`` value, or
        an empty string if no date was given.
    '''
    archive = options[data['archive']['value']] if data.get('archive', {}).get('value') else ''
    year = data.get('end_time', {}).get('value', '')[:4]
    return [archive, year] if archive else []
