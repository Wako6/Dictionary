import json
import requests
import asyncio
import time
import threading
from contextlib import suppress

import settings
from .local_dictionary import LocalDictionary


class Dictionary():
    """ This class handle a database of words
        with them meanings, synonyms ans others informations
        (By default total: 44411 words)

        label: str: Frequent argument that reference word label"""

    # Struture of get_server_state() return
    server_state_model = {
        'server host': settings.DICTIONARY_API_HOST,
        'connected': False,
        'upload speed': None,
        'download speed': None
    }
    _is_pinging = False
    server_infos = None

    def __init__(self, path='dictionary', optimize=True):
        """Create or load a new dictionary.

        *[path] -- Name of database
        *[optimize] -- Optimize size of local database

        """
        if not path:
            raise TypeError('invalid path argument')

        self._name = path
        self._local_db = LocalDictionary(path)
        self._path = self._local_db.get_table_path()

        self._headers = {'Content-Type': 'application/json'}
        self._model = LocalDictionary.DEFAULT_MODEL
        self._optimize = optimize

        self._async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._async_loop)
        self._ping = None

        if Dictionary.server_infos is None:
            Dictionary.server_infos = dict(Dictionary.server_state_model)
            self.get_server_state()  # Get server state

    def __del__(self):
        """Function called when instance is delete."""
        # Close the local database
        self._local_db.close()

        # If this instance launch a pinging to server
        if self._ping is not None and self._ping[0].is_alive():
            # Stop the thread
            self._ping[1].set()

        # Let's also cancel all running tasks:
        pending = asyncio.all_tasks(self._async_loop)
        for task in pending:
            # Now we should await task to execute it's cancellation.
            # Cancelled task raises asyncio.CancelledError
            # that we can suppress:
            with suppress(asyncio.CancelledError):
                self._async_loop.run_until_complete(task)
        self._async_loop.close()

    def __contains__(self, word):
        """Return if word exist in database.

        *word: str/dict: Label or dict with 'label' key

        """
        if isinstance(word, str):
            return len(self.find(label=word, all=True)) > 0
        elif isinstance(word, dict):
            return len(self.find(all=True, **word)) > 0
        else:
            return False  # word type not expected

    def __getitem__(self, label: str):
        """This return only one result.

        *label: Label of searching word

        """
        result = self.find(label, type=None)

        if result:
            # Found something and get first result
            result = result[0]

        return result

    def get_name(self):
        """Return name of used database."""

        return self._name

    def get_server_state(self):
        """Return infos about server state.

        Returned infos is a dict with follow keys:
        *server host -- Name or IP value of host
        *connected -- State of server
        *upload speed -- If 'connected' upload speed
        *download speed -- If 'connected' dowload speed

        """
        # Init the return value
        ret = dict(Dictionary.server_state_model)

        start_time = time.time()
        # Ping server and convert its returned value
        ping_time = float(
            self._async_loop.run_until_complete(
                self._fetch('ping')
            ) or 0
        ) or None

        end_time = time.time()

        if ping_time:
            # Ping success
            ret['connected'] = True
            ret['upload speed'] = ping_time - start_time
            ret['download speed'] = end_time - ping_time
        # Save status un class for others instances know about server status
        Dictionary.server_infos = ret

        return ret

    def find(self, label: str = None, all=False, **kwargs):
        """Return a list of results that matching with label/type.

        *[label] -- Label of searching word, if None try to get in kwargs
        *[all] -- If True, find will add API Dictionary whatever result
        *[kwargs] -- Can be used to search with a 'word' object

        """
        if label is None:
            if 'label' in kwargs:
                # kwargs seems to be like word
                label = kwargs['label']
            else:
                # Impossible to find something
                return None

        if 'type' not in kwargs:
            # Type is filled
            kwargs['type'] = None

        ret = list()
        # Request of API Dictioanry
        fetch_future = None
        if Dictionary.server_infos['connected']:
            # Request the external database
            fetch_future = asyncio.ensure_future(
                self._fetch('unitex', label, gram=kwargs['type']),
                loop=self._async_loop
            )
        elif not Dictionary._is_pinging:
            self._test_connection()
        # Check the local database
        result = self._local_db.find(
                self._create_word(**{
                    'label': label,
                    'type': kwargs['type']
                })
        )

        if result:
            # Word found in local
            ret += result
        if fetch_future:
            # Get result of request
            results = self._async_loop.run_until_complete(fetch_future) or []
            if not result or all:
                for result in results:
                    # result['lem'] = result['lem'] or result['label']
                    result['type'] = result['gram'] or None
                    word = self._create_word(**result)
                    ret.append(word)  # Add result to return value

        return ret or None

    def compose(self, lem: str, **kwargs):
        """Allow to find words according to this infinitive
        and other specifications.

        *lem -- Infinitive form of searched word
        *[type] -- Type of word that need to match to
        *[semantic] -- List of semantic that need to match to
        *[flexional] -- List of flexional that need to match to

        """
        # Initialize additionals matching parameters
        param = dict()
        if 'type' in kwargs:
            param['gram'] = kwargs['type']
        if 'semantic' in kwargs:
            param['semantic'] = kwargs['semantic']
        if 'flexional' in kwargs:
            param['flexional'] = kwargs['flexional']
        # Get results
        fetch_future = None
        if Dictionary.server_infos['connected']:
            # Request the external database
            fetch_future = asyncio.ensure_future(
                self._fetch(
                    'unitex',
                    'compose',
                    lem=lem,
                    **param
                ),
                loop=self._async_loop
            )
        elif not Dictionary._is_pinging:
            self._test_connection()

        ret = list()
        # Check the local database
        result = self._local_db.find(
                self._create_word(**{
                    'lem': lem,
                    **param
                })
        )

        if result:
            ret += result
        if fetch_future:
            # Get result from request
            results = self._async_loop.run_until_complete(fetch_future) or []
            for result in results:
                result['lem'] = result['lem'] or result['label']
                word = self._create_word(**result)
                ret.append(word)  # Add result to return value

        return ret

    def get_infos_on(self, word: dict):
        """Get definitions, synonyms, and others datas on 'word'.

        *word -- One result of find() or __getitem__()

        """
        if not Dictionary.server_infos['connected']:
            # Cannot access to extarnal database
            self._test_connection()
            return
        elif 'isFetched' in word and word['isFetched']:
            # This world is already fetched
            return

        # Request the datas from internet
        fetch_future = self._async_loop.ensure_future(
            self._fetch(
                'dictionary',
                word['lem'] or word['label'],
                type=word['type']
            ),
            loop=self._async_loop
        )
        # Get result of request
        results = self._async_loop.run_until_complete(fetch_future) or []
        for result in results:
            result['isFetched'] = True
            self.update(
                result,
                word,
                overwrite=False,
                insertable=False
            )

    def beautify(self, word: dict):
        """Return word repr, it remove keys with empty value.

        *word -- One result of find() or __getitem__()

        """
        if word is None:
            return None

        ret = dict()
        for k in self._model.keys():
            if word[k]:  # Parse keys with non-empty value
                ret[k] = word[k]

        if word['isPersistent']:
            del ret['_id']
            del ret['isPersistent']

        return ret

    def insert(self, force=False, **kwargs):
        """Save a new word in the database and return it.

        *word -- One result of find() or __getitem__()
        *[force] -- If True and word is already exist, insert will
                    make a copy and save it
        *[kwargs] -- Others attribute of word

        """
        if 'label' not in kwargs or not kwargs['label']:
            raise KeyError("no 'label' found, cannot insert this word")

        word = self._create_word(**kwargs)

        if word['isPersistent']:
            if not force:
                # Can not insert, it seems to already be in the database
                try:
                    # Touch word
                    self._local_db.find(word)
                except Exception as e:
                    raise e
                finally:
                    return
            # Force the insertion
            word['isPersistent'] = False

        # Insert in database
        self._local_db.insert(word)

        return word

    def update(self, kw: dict, word: dict, overwrite=True, insertable=True):
        """Allow to update some field of 'word'.

        *kw -- Keys, Values to update
        *word -- One result of find() or __getitem__()
        *[overwrite] -- Replace existing value by new value, else try to add it
        *[insertable] -- Save it in database if True

        """
        tmp_kw = dict(kw)
        # Control is '_id' and 'isPersistent' try to be manually update
        if '_id' in kw:
            del tmp_kw['_id']
        if 'isPersistent' in kw:
            del tmp_kw['isPersistent']

        if overwrite:
            # Replace values
            for key in tmp_kw.keys():
                if key in word:
                    word[key] = kw[key]
        else:
            # Try to adding value
            self._copy_word(
                    tmp_kw,
                    word,
                    exceptions=[
                        'label',
                        'type'
                    ]
                )

        if word['isPersistent']:
            # Update database
            self._local_db.update(word, word)
        elif insertable:
            # Insert the update in the database
            self._local_db.insert(word)

    def add_sens(
        self, word: dict, definition: str,
        examples: list = [], synonyms: list = []
    ):
        """Insert a sens into word.

        *word -- One result of find() or __getitem__()
        *definition -- Sens' description
        *[examples] -- List of examples
        *[synonyms] -- List of synonyms

        """
        # Initialize sens structure
        sens = {
            'definition': definition,
            'examples': examples,
            'synonyms': synonyms
        }

        self.update({'sens': [sens]}, word, overwrite=False)

    def add_quote(
        self, word: dict, quote: str,
        author: str = None, infos: str = None, infosAuthor: str = None
    ):
        """Insert a quote into word.

        *word -- One result of find() or __getitem__()
        *quote -- The quote
        *[author] -- Author name
        *[infos] -- Infos on the quote
        *[infosAuthor] -- Infos author's quote

        """
        # Initialize sens structure
        quote = {
            'text': quote,
            'author': author,
            'infos': infos,
            'infosAuthor': infosAuthor
        }

        self.update({'quotes': [quote]}, word, overwrite=False)

    def add_difficulty(self, word: dict, d_type: str, d_text: str):
        """Insert a difficulty into word.

        *word -- One result of find() or __getitem__()
        *d_type -- Type of the difficulty
        *d_text -- Description of difficulty

        """
        # Initialize sens structure
        difficulty = {
            'type': d_type,
            'text': d_text
        }

        self.update({'difficulties': [difficulty]}, word, overwrite=False)

    def get_group_of(self, word: dict):
        """[WARNING] Return synonyms group of word.
        (Coming soon...)

        *word -- One result of find() or __getitem__()

        """
        print('[WARNING] This function is in contruction ...')
        pass

    def _create_word(self, **kwargs):
        """Create and init structure of word.

        *[kwargs] -- Attributes of word

        """
        new_word = dict(self._model)
        # Initialize values of word according to parameters
        for k in kwargs.keys():
            new_word[k] = kwargs[k]

        return new_word

    def _get_srv_avg_latence(self, word_list: list = None):
        """Calculate average latence to request.

        *word_list] -- List of word to search on external database
                       for the calculation
        
        """
        if not Dictionary.server_infos['connected']:
            # Cannot access to the external database
            return None

        if not word_list:
            # No word list specified
            word_list = [
                'dictionnaire',
                'ranger',
                'être',
                'indispensable'
            ]

        start_time = time.time()
        for label in word_list:
            # Request extarnal database
            asyncio.run(
                self._fetch('dictionary', label)
            )

        return (time.time() - start_time) / len(word_list)

    def _copy_word(self, word_src, word_dst, exceptions=[]):
        """Update a word by adding values if possible else replace it."""
        for k, v in word_src.items():
            if k in exceptions:
                # key must not be update
                continue
            if k in word_dst:
                if not isinstance(v, type(word_dst[k])):
                    # Not the same type
                    word_dst[k] = v
                elif isinstance(v, list):
                    word_dst[k] += v
                elif isinstance(v, dict):
                    word_dst[k] = word_dst[k] | v
                else:
                    # Cannot add the value
                    word_dst[k] = v
            else:
                # Add value
                word_dst[k] = v

    async def _fetch(self, *args, **kwargs):
        """Allow to request external server."""
        def kwargs_to_url(key, arg):
            """Translate kwargs argument in url syntax."""
            try:
                arg = arg.strip()
            except Exception:
                pass
            return '{}={}'.format(key, arg)

        # Initialize additionals str_kwargs paramaters (kwargs)
        str_kwargs = list()
        # Translate kwargs argument in url syntax
        for k, arg in kwargs.items():
            if isinstance(arg, list):
                for elem in arg:
                    str_kwargs.append(kwargs_to_url(k, elem))
            else:
                str_kwargs.append(kwargs_to_url(k, arg))

        str_kwargs = '?{}'.format(
                    '&'.join(str_kwargs)
                )
        # Construct the URL for request API
        api_url = '{}/{}{}'.format(
            settings.DICTIONARY_API_URL,
            '/'.join(args),
            str_kwargs if str_kwargs != '?' else ''
        )
        try:
            # Request the API Dictionary
            response = requests.get(api_url, headers=self._headers)

            if response.status_code == 200:
                # API response with no error
                return json.loads(response.content.decode('utf-8'))
        except requests.exceptions.ConnectionError:
            pass

        Dictionary.server_infos['connected'] = False
        self._test_connection()

        return None

    def _test_connection(self):
        """Allow to launch a process that try to access to server."""
        if Dictionary.server_infos['connected'] or Dictionary._is_pinging:
            # Is already connected or pinging
            return

        Dictionary._is_pinging = True
        self._ping_server()

    def _ping_server(self):
        """Allow to initialize pinging thread and start it."""
        def _ping_server_aux(e):
            connected = False
            waiting_time = 1  # Seconds

            while not e.isSet():
                # Ping the server
                ping_time = float(
                    asyncio.run(
                        self._fetch('ping')
                    ) or 0
                ) or None
                connected = ping_time is not None

                if connected:
                    # Connection is etablished with sucess
                    e.set()
                    Dictionary.server_infos['connected'] = True
                    break
                # Sleep and wait a potential signal
                e.wait(waiting_time)
                waiting_time *= (12 / 9)  # Extend sleeping time

            Dictionary._is_pinging = False

            if self._optimize:
                # Calculate speed of server requesting (by default 4 words)
                server_rq_speed = self._get_srv_avg_latence()
                # Set find time optimization
                self._local_db.find_time_opti = server_rq_speed

        event = threading.Event()  # Init the stopping event
        thread = threading.Thread(  # Create the pinging thread
            name='ping-server',
            target=_ping_server_aux,
            args=(event, )
        )
        self._ping = (thread, event)
        thread.setDaemon(True)
        thread.start()
