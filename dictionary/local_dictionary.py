from tinydb import Query
from datetime import datetime
import os
import time

from .storage import Table
import settings


class LocalDictionary():
    """This class allow to manage local database of dictionary."""

    DEFAULT_MODEL = {
            'label': None,
            'type': None,
            'lem': None,
            'tags': None,
            'flexional': [],
            'semantic': [],
            'sens': [],
            'homonyms': [],
            'homonymsVar': [],
            'difficulties': [],
            'quotes': [],
            'isPersistent': False
        }

    def __init__(self, dictionary_name='dictionary',
                 find_time_opti: float = None):
        # Create or open database
        self._db = Table(table_name=dictionary_name)
        self._path = self._db.get_table_path()  # Get database path
        self._size = os.path.getsize(self._path)  # Database file size
        self._len = len(self._db)  # Count of word in database
        self.find_time_opti = find_time_opti  # Max of time for find request
        # (sum of find speed, count find speed sumed)
        self._find_speed = (0, 0)
        # Factor to get a sample of find speed
        self._sample_find_speed = True

        if self._size - settings.LOCAL_DICT_MAX_SIZE > 0:
            # size of file database is greater than (5Mb)
            self._clean_oldest()

    def __len__(self):
        self._len = len(self._db)
        return self._len

    def __del__(self):
        """Close the database"""
        self.close()

    def get_table_path(self):
        return self._path

    def get_average_latence(self, word_list: list = None):
        if not word_list:
            word_list = [
                'dictionnaire',
                'ranger',
                'être',
                'indispensable'
            ]

        start_time = time.time()
        for label in word_list:
            word = dict(self.DEFAULT_MODEL)
            word['label'] = label
            self.find(word)

        return (time.time() - start_time) / len(word_list)

    def find(self, word):
        def list_contains(lst, *sub):
            """ Return if 'lst' contains a list or a list of list
                that contain 'sub'
            """
            if len(lst) < len(sub):
                return False
            elif lst and isinstance(lst[0], list):
                return all([any([x in _l for _l in lst]) for x in sub])
            else:
                return all([x in lst for x in sub])

        start_time = time.time()
        Word = Query()
        query = None
        for key in self.DEFAULT_MODEL.keys():
            if word[key]:
                if isinstance(self.DEFAULT_MODEL[key], list) and \
                   key in ['flexional', 'semantic']:
                    tmp_query = (getattr(Word, key).test(
                        list_contains,
                        *word[key]
                    ))
                else:
                    tmp_query = (getattr(Word, key) == word[key])

                if query is None:
                    # Initialize the query
                    query = tmp_query
                else:
                    query = (query & tmp_query)

        results = self._db.search(query)

        if results:
            # Elements found
            for result in results:
                self._update_clock(result, persistent=True)
                del result['clock']

        execution_time = time.time() - start_time
        if self.find_time_opti and self._sample_find_speed:
            self._find_speed_tracing(execution_time)

        return results

    def _find_speed_tracing(self, delay):
        # Find time optimization is up
        total_time, count = self._find_speed
        total_time += delay
        count += 1
        # Update find speed variable
        self._find_speed = (total_time, count)
        self._sample_find_speed = False
        # Calculate average find speed
        find_speed = total_time / count
        if find_speed > self.find_time_opti:
            self._clean_oldest()
            self._find_speed = (0, 0)

    def insert(self, word):
        if word['isPersistent']:
            raise KeyError("invalid action, try to adding an existint")
        # Adding 'clock' value
        word['clock'] = None
        # Adding print to this object, has saved in local
        word['isPersistent'] = True
        word['_id'] = id(word)
        # Insert in database
        self._db.insert(word)
        # Adding 'clock' value
        self._update_clock(word, persistent=True)
        del word['clock']

        # Update size of file database variable
        self._size = os.path.getsize(self._path)
        self._len = len(self._db)
        # Active get find speed
        self._sample_find_speed = True

        if self._size - settings.LOCAL_DICT_MAX_SIZE > 0:
            # size of file database is greater than 5M
            self._clean_oldest()

    def update(self, kw, word):
        if not word['isPersistent']:
            raise KeyError("invalid 'word' argument, cannot update")

        Word = Query()
        if 'clock' in kw:
            # External cannot edit clock value
            del kw['clock']

        # Update matching word from database
        self._db.update(
            kw,
            Word._id == word['_id']
        )
        # Update 'clock' value
        self._update_clock(word, persistent=True)
        del word['clock']
        # Active get find speed
        self._sample_find_speed = True

    def remove(self, word):
        if ('isPersistent' in word and not word['isPersistent']) or \
                '_id' not in word:
            raise KeyError("invalid 'word' argument, cannot remove")

        Word = Query()
        # Remove matching word from database
        self._db.remove(
            Word._id == word['_id']
        )
        # Remove print to this object
        word['isPersistent'] = False
        del word['_id']
        # Re-evaluated values
        self._size = os.path.getsize(self._path)
        self._len = len(self._db)
        # Active get find speed
        self._sample_find_speed = True

    def _update_clock(self, word, persistent=False):
        # Add or update 'clock' field
        word['clock'] = datetime.now()

        if persistent and word['isPersistent']:
            # Save in database
            # Update matching word from database
            Word = Query()
            self._db.update(
                {'clock': datetime.timestamp(word['clock'])},
                Word._id == word['_id']
            )

    def _clean_oldest(self):
        datas = self._db.all()
        min_count = settings.LOCAL_DICT_MIN_COUNT
        self._size = os.path.getsize(self._path)
        final_size = int(float(self._size) * settings.LOCAL_DICT_CLEAN_COEF)

        for word in sorted(
            datas,
            key=lambda word: word['clock']
        ):
            # Remove oldest item
            self.remove(word)

            if len(self) <= min_count:
                # Number of items min has been reached
                break
            elif self._size - final_size <= 0:
                # Size of file is correctly reduce
                break

    def all(self):
        return self._db.all()

    def purge(self):
        self._db.truncate()
        # Reinitialize instance value
        self._size = os.path.getsize(self._path)
        self._len = len(self._db)
        self._find_speed = (0, 0)
        self._sample_find_speed = True

    def close(self):
        self._db.close()
