import json
import requests
import asyncio

from variables import Variables
from .local_dictioanry import LocalDictionary


class Dictionary():
    """ This class handle a database of words
        with them meanings, synonyms ans others informations
        (By default total: 44411 words)

        @label: str: Frequent argument that reference word label"""

    def __init__(self, path='dictionary'):
        """
            *path: Name of database
        """

        if not path:
            raise TypeError('invalid path argument')

        self._name = path
        self._local_db = LocalDictionary(path)
        self._path = self._local_db.get_table_path()

        self._headers = {'Content-Type': 'application/json'}
        self._model = LocalDictionary.DEFAULT_MODEL

    def __getitem__(self, label: str):
        """This return only one result

            @label: label of searching word
        """

        result = self.find(label)

        if result:
            result = result[0]

        return result

    def get_name(self):
        """Return name of used database"""

        return self._name

    def insert(self, word: dict, force=False):
        """Allow to save a new word in the database

            @word: One result of find() or __getitem__()
            force: If True and word is already exist, insert will
                   make a copy and save it
        """

        if not word['label']:
            raise KeyError("no 'label' found, cannot insert this word")
        elif word['isPersistent'] and not force:
            # this word already exist in database
            try:
                # Touch word
                self._local_db._update_clock(word, persistent=True)
            except Exception as e:
                raise e
            raise KeyError('this word is already exists in database')

        new_word = self._create_word(word)

        if word['isPersistent']:
            # force the insert
            new_word['isPersistent'] = False
        # Insert in database
        self._local_db.insert(new_word)

        return new_word

    def update(self, kw: dict, word: dict):
        """Allow to update some field of 'word'

            @kw: Keys, Values to update
            @word: One result of find() or __getitem__()
        """

        # Update database
        if word['isPersistent']:
            self._local_db.update(kw, word)
        # Update temp value
        for key in kw.keys():
            if key in word:
                word[key] = kw[key]

        return word

    def find(self, label: str = None, all=False, **kwargs):
        """Return a list of results

            @label: label of searching word, if None try to get in kwargs
            *all: If True, find will add API Dictionary whatever result
            **kwargs: Can be used to search with a 'word' object
        """

        if label is None:
            if 'label' in kwargs:
                # kwargs seems to be like word
                label = kwargs['label']
            else:
                # Impossible to find something
                return None

        ret = list()
        # Request of API Dictioanry
        fetch_promise = self._fetch('unitex', label, type=kwargs['type'])

        result = self._local_db.find({
            'label': label,
            'type': kwargs['type']
        })

        if result:
            # Word found in local
            ret.append(result)
        if not result or all:
            # Get response of search
            results = asyncio.run(fetch_promise)
            for result in results:
                result['lem'] = result['lem'] or result['label']
            ret += results  # Add results to return value

        return ret

    def beautify(self, word: dict):
        """Return word repr, keys with non-empty value

           @word: One result of find() or __getitem__()
        """

        ret = dict()
        for k, v in word.items():
            if v:  # Parse keys with non-empty value
                ret[k] = v

        if word['isPersistent']:
            del ret['_id']
            del ret['isPersistent']

        return ret

    def add_sens(
        self, word: dict, definition: str,
        examples: list = None, synonyms: list = None
    ):
        """ Insert a sens into word

            @word: One result of find() or __getitem__()
            @definition: Sens' description
            *examples: List of examples
            *synonyms: List of synonyms
        """

        # Initialize sens structure
        sens = {
            'definition': definition,
            'examples': examples,
            'synonyms': synonyms
        }

        if word['sens'] is None:
            word['sens'] = list()
        # Add sens to list of sens
        word['sens'].append(sens)

        if word['isPersistent']:
            # 'word' is persistent
            self.update({'sens': word['sens']}, word)
        else:
            # 'word' is not persistent
            self.insert(word)  # Make it be persistent

    def add_quote(
        self, word: dict, quote: str,
        author: str = None, infos: str = None, infosAuthor: str = None
    ):
        """ Insert a quote into word

            @word: One result of find() or __getitem__()
            @quote: The quote
            *author: Author name
            *infos: Infos on the quote
            *infosAuthor: Infos author's quote
        """

        # Initialize sens structure
        quote = {
            'text': quote,
            'author': author,
            'infos': infos,
            'infosAuthor': infosAuthor
        }

        if word['quotes'] is None:
            word['quotes'] = list()

        word['quotes'].append(quote)

        if word['isPersistent']:
            # 'word' is persistent
            self.update({'sens': word['quotes']}, word)
        else:
            # 'word' is not persistent
            self.insert(word)  # Make it be persistent

    def add_difficulty(self, word: dict, d_type: str, d_text: str):
        """ Insert a difficulty into word

            @word: One result of find() or __getitem__()
            @d_type: Type of the difficulty
            @d_text: Description of difficulty
        """

        # Initialize sens structure
        difficulties = {
            'type': d_type,
            'text': d_text
        }

        if word['difficulties'] is None:
            word['difficulties'] = list()

        word['difficulties'].append(difficulties)

        if word['isPersistent']:
            # 'word' is persistent
            self.update({'sens': word['difficulties']}, word)
        else:
            # 'word' is not persistent
            self.insert(word)  # Make it be persistent

    def compose(
        self, lem: str,
        gram: str = None, sem: list = None, flex: list = None
    ):
        """ Allow to find words according to this infinitive
            and other specifications

            @lem: Infinitive form of searched word
            *gram: Falcultative argument for type
            *semantic: List of semantic that need to match to
            *flexional: List of flexional that need to match to
        """

        # Initialize additionals matching parameters
        kwargs = dict()
        if gram:
            kwargs['gram'] = gram
        if sem:
            kwargs['semantic'] = sem
        if flex:
            kwargs['flexional'] = flex
        # Get results
        compose_promise = self._fetch(
            'unitex',
            'compose',
            lem=lem,
            **kwargs
        )

        return asyncio.run(compose_promise)

    def get_infos_on(self, word: dict):
        """Return definitions, synonyms, and others datas on 'word'

            @word: One result of find() or __getitem__()
        """
        # Initialize sens structure
        fetch_promise = self._fetch(
            'dictionary',
            word['lem'],
            type=word['type']
        )

        results = asyncio.run(fetch_promise)

        if results:
            for result in results:
                tmp_word = dict(word)
                LocalDictionary._copy_word(
                    result,
                    tmp_word,
                    exceptions=[
                        'label',
                        'type',
                    ]
                )
                if word['isPersistent']:
                    self._local_db.update(tmp_word, word)
                else:
                    w = self.update(tmp_word, word)
                    word = self.insert(w)

        return word

    def get_group_of(self, word: dict):
        """[WARNING] Return synonyms group of word
            (Coming soon...)

            @word: One result of find() or __getitem__()
        """

        print('[WARNING] This function is in contruction ...')
        pass

    def _create_word(self, **kwargs):
        new_word = dict(self._model)
        # Initialize values of word according to parameters
        return self.update(kwargs, new_word)

    async def _fetch(self, *args, **kwargs):
        # Initialize additionals query paramaters (kwargs)
        query = list()
        for k, arg in kwargs.items():
            if isinstance(arg, list):
                for elem in arg:
                    query.append('{}={}'.format(k, elem.strip()))
            else:
                query.append('{}={}'.format(k, arg.strip()))

        query = '?{}'.format(
                    '&'.join(query)
                )
        # Construct the URL for request API
        api_url = '{}/{}{}'.format(
            Variables.DICTIONARY_API_URL,
            '/'.join(args),
            query if query != '?' else ''
        )

        # Request the API Dictionary
        response = requests.get(api_url, headers=self._headers)

        if response.status_code == 200:
            # API response with no error
            return json.loads(response.content.decode('utf-8'))
        else:
            # An error is occured
            return None
