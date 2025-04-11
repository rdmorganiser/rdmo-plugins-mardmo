import os
import json
from functools import lru_cache

# Map of question section identifiers to relative paths
DATA_PATHS = {
    'algorithm': 'algorithm/data/questions.json',
    'model': 'model/data/questions.json',
    'publication': 'publication/data/questions.json',
    'workflow': 'workflow/data/questions.json',
}

@lru_cache()
def get_questions(section: str) -> dict:
    """Lazily load and cache question data from JSON files."""
    if section not in DATA_PATHS:
        raise ValueError(f"Unknown section '{section}'")

    file_path = os.path.join(os.path.dirname(__file__), DATA_PATHS[section])
    with open(file_path, "r") as json_file:
        return json.load(json_file)

def get_questionsWO() -> dict:
    """Retrieve the questions dictionary from MaRDMOConfig."""
    return get_questions('workflow')

def get_questionsAL() -> dict:
    """Retrieve the questions dictionary from MaRDMOConfig."""
    return get_questions('algorithm')

def get_questionsMO() -> dict:
    """Retrieve the questions dictionary from MaRDMOConfig."""
    return get_questions('model')

def get_questionsPU() -> dict:
    """Retrieve the questions dictionary from MaRDMOConfig."""
    return get_questions('publication')
