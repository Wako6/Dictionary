

CODES = dict()
CODES['gram'] = {
        'A': 'adjectif',
        'ADV': 'adverbe',
        'CONJC': 'conjonction de coordination',
        'CONJS': 'conjonction de subordination',
        'DET': 'déterminant',
        'INTJ': 'interjection',
        'N': 'nom',
        'PREP': 'préposition',
        'PRO': 'pronom',
        'V': 'verbe'
    }
CODES['semantic'] = {
    'z1': 'langage courant',
    'z2': 'langage spécialisé',
    'z3': 'langage très spécialisé',
    'Abst': 'abstrait',
    'Anl': 'animal',
    'AnlColl': 'animal collectif',
    'Conc': 'concret',
    'ConcColl': 'concret collectif',
    'Hum': 'humain',
    'HumColl': 'humain collectif',
    't': 'verbe transitif',
    'i': 'verbe intransitif',
    'en': 'particule pré-verbale obligatoire',
    'se': 'verbe pronominal',
    'ne': 'verbe à négation obligatoire'
    }
CODES['flexional'] = {
    'm': 'masculin',
    'f': 'féminin',
    'n': 'neutre',
    's': 'singulier',
    'p': 'pluriel',
    '1': '1st personne',
    '2': '2nd personne',
    '3': '3rd personne',
    'P': 'présent de l’indicatif',
    'I': 'imparfait de l’indicatif',
    'S': 'présent du subjonctif',
    'T': 'imparfait du subjonctif',
    'Y': 'présent de l’impératif',
    'C': 'présent du conditionnel',
    'J': 'passé simple',
    'W': 'infinitif',
    'G': 'participe présent',
    'K': 'participe passé',
    'F': 'futur'
    }


def get_code_of(tag):
    """Return code that matching with tag"""

    for section, codes in CODES.items():
        if tag in codes:
            return codes[tag]

    return None
