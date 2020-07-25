from tinydb import Query
from .storage import Table
import os

"""
    NUMBERS OF WORDS BY CATEGORY
    ============================
    unitex/name: 4 607
    unitex/a: 59 960
    unitex/b: 35 229
    unitex/c: 74 045
    unitex/d: 88 607
    unitex/e: 42 630
    unitex/f: 26 580
    unitex/g: 22 607
    unitex/h: 17 638
    unitex/i: 23 156
    unitex/j: 5 386
    unitex/k: 1 403
    unitex/l: 18 208
    unitex/m: 39 046
    unitex/n: 11 121
    unitex/o: 12 572
    unitex/p: 68 639
    unitex/q: 2 620
    unitex/r: 102 682
    unitex/s: 49 909
    unitex/t: 34 866
    unitex/u: 3 124
    unitex/v: 15 756
    unitex/w: 457
    unitex/x: 572
    unitex/y: 443
    unitex/z: 1 728
    unitex/à: 2 043
    unitex/â: 172
    unitex/ç: 14
    unitex/è: 33
    unitex/é: 26 209
    unitex/ê: 27
    unitex/î: 121
    unitex/ï: 4
    unitex/ô: 45
    unitex/ö: 1
    ----------------------------
    total: 792 260 words
"""


class Unitex:
    """Class allow to handle a set of database like one dictionary"""

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

    """ Initialize the unitex dataset
        @source : str : Folder name of the set of database
                        (allow unitex annotation only)
    """
    def __init__(self, source='unitex'):
        self._source = source

        # Optimizations
        self.table_name = None
        self.bdd = None

    """ Check if dataset contains one word
        @str_word : str : Label of word
    """
    def __contains__(self, str_word):
        bdd = self._getTableByWord(str_word)
        Word = Query()
        return bdd._db.contains(Word.label == str_word)

    """ Access to all dataset easily by using self
        @str_word : str : Label of word
    """
    def __getitem__(self, str_word):
        bdd = self._getTableByWord(str_word)
        Word = Query()
        return bdd.find(Word.label == str_word)

    """ Return path and name of dataset concerned
        @str_word : str : Label of word
    """
    def _getTableNameByWord(self, str_word):
        if str_word[0] == str_word[0].upper():
            # str_word's first letter is major
            return os.path.join(self._source, 'name')
        else:
            if str_word[0].isalpha():
                return os.path.join(self._source, str_word[0])

    """ Load the dataset concerned by str_word
        @str_word : str : Label of word
    """
    def _getTableByWord(self, str_word):
        _tn = self.table_name
        self.table_name = self._getTableNameByWord(str_word)

        if _tn != self.table_name:
            # Database requested is different
            self.bdd = Table(self.table_name)

        return self.bdd

    """ Return label of the grammatical code
        @code : str : unitex annotation
    """
    def getGram(self, code):
        return self.CODES['gram'][code]

    """ Return label of the semantic code
        @code : str : unitex annotation
    """
    def getSemantic(self, code):
        return self.CODES['semantic'][code]

    """ Return label of the flexional code
        @code : str : unitex annotation
    """
    def getFlexional(self, code):
        return self.CODES['flexional'][code]

    """ Return infinitive form of str_word
        @str_word : str : Label of word
    """
    def lemmatize(self, str_word):
        if str_word not in self:
            return None

        result = self[str_word][0]['lem']
        if result == '' or result is None:
            result = self[str_word][0]['label']
        return result

    """ Return type of word
        @str_word : str : Label of word
    """
    def getType(self, str_word):
        if str_word not in self:
            return None

        return self.getGram(self[str_word][0]['gram'])

    def getTags(self, str_word):
        if str_word not in self:
            return None

        pass
