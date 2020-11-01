from tinydb import Query
from datetime import datetime
import os

from .storage import Table
from variables import Variables


class LocalDictionary():
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

    def __init__(self, dictionary_name='dictionary'):
        self._db = Table(table_name=dictionary_name)
        self._path = self._db.get_table_path()
        self._size = os.path.getsize(self._path)
        self._len = len(self._db)

        if self._size - Variables.LOCAL_DICT_MAX_SIZE > 0:
            # size of file database is greater than (5Mb)
            self._clean_oldest()

    def __len__(self):
        self._len = len(self._db)
        return self._len

    def get_table_path(self):
        return self._path

    def find(self, word):
        Word = Query()
        results = None
        # Searching word
        if word['type']:
            results = self._db.search(
                (Word.label == word['label']) &
                (Word.gram == word['label'])
            )
        else:
            results = self._db.search(Word.label == word['label'])

        if results:
            # elements found
            for result in results:
                self._update_clock(result, persistent=True)
                del result['clock']

        return results

    def insert(self, word):
        if word['isPersistent']:
            raise KeyError("invalid action, try to adding an existint")
        # Adding 'clock' value
        self._update_clock(word)
        # Adding print to this object, has saved in local
        word['isPersistent'] = True
        word['_id'] = id(word)
        # Insert in database
        self._db.insert(word)

        # Update size of file database variable
        self._size = os.path.getsize(self._path)
        self._len = len(self._db)

        if self._size - Variables.LOCAL_DICT_MAX_SIZE > 0:
            # size of file database is greater than 5M
            self._clean_oldest()

    def update(self, kw, word):
        if not word['isPersistent']:
            raise KeyError("invalid 'word' argument, cannot update")

        Word = Query()
        # Update 'clock' value
        self._update_clock(word)
        if 'clock' in kw:
            # External cannot edit clock value
            del kw['clock']
        # Update matching word from database
        self._db.update(
            kw,
            Word._id == word['_id']
        )

    def remove(self, word):
        if not word['isPersistent']:
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

    def _update_clock(self, word, persistent=False):
        # Add or update 'clock' field
        word['clock'] = datetime.now()

        if persistent and word['isPersistent']:
            # Save in database
            self.update({'clock': word['clock']}, word)

    def _clean_oldest(self):
        datas = self._db.all()
        min_count = Variables.LOCAL_DICT_MIN_COUNT
        final_size = self._size * Variables.LOCAL_DICT_CLEAN_COEF

        for word in sorted(
            datas,
            key=lambda word: word['clock'],
            reverse=True
        ):
            # Remove oldest item
            self.remove(word)

            if self._len < min_count:
                # Number of items min has been reached
                break
            elif self._size - final_size <= 0:
                # Size of file is correctly reduce
                break

    def _copy_word(self, word_src, word_dst, exceptions=[]):
        for k, v in word_src.items():
            if k in exceptions:
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
                    word_dst[k] = v
            else:
                word_dst[k] = v
