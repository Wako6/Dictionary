from tinydb import Query
from .storage import Table
from variables import Variables
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
        @str_word : Label of word
    """
    def __contains__(self, str_word: str):
        bdd = self._getTableByWord(str_word)
        Word = Query()
        return bdd._db.contains(Word.label == str_word)

    """ Access to all dataset easily by using self
        @str_word : Label of word
    """
    def __getitem__(self, str_word: str):
        bdd = self._getTableByWord(str_word)
        Word = Query()
        return bdd.find(Word.label == str_word)

    """ Return path and name of dataset concerned
        @str_word : Label of word
    """
    def _getTableNameByWord(self, str_word: str):
        if str_word[0] == str_word[0].upper():
            # str_word's first letter is uppercase
            return os.path.join(self._source, 'name')
        else:
            if str_word[0].isalpha():
                return os.path.join(self._source, str_word[0])

    """ Load the dataset concerned by str_word
        @str_word : Label of word
    """
    def _getTableByWord(self, str_word: str):
        _tn = self.table_name
        self.table_name = self._getTableNameByWord(str_word)

        if _tn != self.table_name:
            # Database requested is different
            self.bdd = Table(self.table_name)

        return self.bdd

    """ Return label of the grammatical code
        @code : Unitex annotation
    """
    def getGrammaticalCode(self, code: str):
        if code not in self.CODES['gram']:
            return None

        return self.CODES['gram'][code]

    """ Return label of the semantic code
        @code : Unitex annotation
    """
    def getSemanticCode(self, code: str):
        if code not in self.CODES['semantic']:
            return None

        return self.CODES['semantic'][code]

    """ Return label of the flexional code
        @code : Unitex annotation
    """
    def getFlexionalCode(self, code: str):
        if code not in self.CODES['flexional']:
            return None

        return self.CODES['flexional'][code]

    """ Return infinitive form of str_word
        @str_word : Label of word
    """
    def lemmatize(self, str_word: str):
        # Check if Unitex database contain str_word
        if str_word not in self:
            return None

        result = self[str_word]
        # Get lem of all result
        ret = [res['lem'] for res in result]

        if ret == [] or ret is None:
            # In case if no lem found
            ret = [lem['label'] for lem in result]

        return ret

    """ Return type of word
        @str_word : Label of word
    """
    def getType(self, str_word: str):
        if str_word not in self:
            return None

        result = self[str_word]
        return [self.getGrammaticalCode(t['gram']) for t in result]

    """ Return flexional of word
        @str_word : Label of word
    """
    def getFlexional(self, str_word: str):
        if str_word not in self:
            return None

        result = self[str_word]
        ret = list()
        # Get all flexionals in result
        for e in result:
            ret += e['flexional']
        # Remove duplicates value in ret List
        return list(dict.fromkeys(ret))

    """ Return semantic of word
        @str_word : Label of word
    """
    def getSemantic(self, str_word: str):
        if str_word not in self:
            return None
        # Get object word 
        result = self[str_word]
        ret = list()
        for e in result:
            # Keep semantic code
            ret += e['semantic']
        # Remove duplicates value from ret
        return list(dict.fromkeys(ret))

    """ Translate list of semantic codes
        @semanticCodes : Semantic codes
    """
    def translateSemantics(self, semanticCodes: list):
        ret = list()
        for code in semanticCodes:
            ret.append(self.getSemanticCode(code))

        return ret

    """ Translate a flexional code
        @flexionalCode : Flexional code
    """
    def translateFlexional(self, flexionalCode: str):
        ret = list()
        for code in flexionalCode:
            ret.append(self.getFlexionalCode(code))

        return ret

    """ Translate list of flexional codes
        @flexionalCodes : Flexional codes
    """
    def translateFlexionals(self, flexionalCodes: list()):
        ret = list()
        for flexionalCode in flexionalCodes:
            ret.append(self.translateFlexional(flexionalCode))

        return ret

    """ Return the word that matching with parameters
        @lem : Lemmatization of the researched word
        @gram : Grammatical of the researched word
        @sem : Semantic of the researched word
        @flex : Flexional of the researched word
    """
    def compose(self, lem: str, gram: str, sem: str, flex: str):
        Word = Query()
        request = None

        def addRequest(query):
            global request
            request = ((request) & (query)) if request is not None else query

        if lem is not None:
            addRequest((Word.lem == lem))

        if gram is not None:
            addRequest((Word.gram == gram))

        # if sem is not None:
        #     addRequest((Word.semantic.any([sem])))

        # if flex is not None:
        #     addRequest((Word.flexional.any([flex]))

        return self.search(request)

    """ Search with an expression across datasets
        @expression : Query Object Expression
    """
    def search(self, expression: Query):
        save_table_name = self.table_name  # Save dataset
        save_bdd = self.bdd

        ret = list()
        for _, _, files in os.walk(os.path.join(Variables.DATABASE_PATH, self._source)):
            for filename in files:
                if filename is None:
                    continue

                self.table_name = os.path.join(self._source, filename.split('.', 1)[0])
                self.bdd = Table(self.table_name)
                ret += self.bdd._db.search(expression)
        # Reload previous used dataset
        self.table_name = save_table_name
        self.bdd = save_bdd
        return ret
