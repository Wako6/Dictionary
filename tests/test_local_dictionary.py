import unittest
import os.path

from dictionary import LocalDictionary
import settings


class LocalDictionaryTest(unittest.TestCase):
    """Test case utilisé pour tester les fonctions du module
    'local-dictionary'.

    """

    def setUp(self):
        """Initialization of test and insert a word."""
        self.database_name = 'local-dictionary-test'
        self.db = LocalDictionary(
            dictionary_name=self.database_name
        )

        self.inserted_word_label = 'my test'
        self.word = dict(self.db.DEFAULT_MODEL)
        self.word['label'] = self.inserted_word_label
        self.db.insert(self.word)

    def tearDown(self):
        """Cleaning of resources created for tests."""
        path = ''
        if self.db is not None:
            path = self.db.get_table_path()
        else:
            import settings
            path = os.path.join(
                settings.DATABASE_PATH,
                self.database_name
            )
        self.db.close()
        del self.db
        if path:
            os.remove(path)

    def test_init_and_get_path(self):
        """Test the well working of  '__init__'
        and get 'get_table_path'.

        """
        self.assertTrue(
            self.db is not None,
            'Test if initialization doing well'
        )

        path = self.db.get_table_path()
        self.assertTrue(
            os.path.exists(path),
            'Test if database is create'
        )

    def test_insert_len_and_purge(self):
        """Test on correct insert, len and purge of dictonary."""
        self.assertEqual(len(self.db), 1, 'Test get len of dictionary')

        # Remove all element save in database
        self.db.purge()

        self.assertEqual(len(self.db), 0, 'Test get len of dictionary')

    def test_find_word(self):
        """Test to find element in dictionary."""
        # Creating a object to search
        search_word = dict(self.db.DEFAULT_MODEL)
        search_word['label'] = self.word['label']
        # Search word in database
        find_words = self.db.find(search_word)

        self.assertTrue(find_words and
                        find_words[0]['label'] == self.word['label'])
        self.assertTrue(find_words[0]['_id'] == self.word['_id'])

    def test_update_word(self):
        """Test well working of 'update' function."""
        change = {
            'type': 'test'
        }
        self.db.update(change, self.word)

        # Creating a object to search
        search_word = dict(self.db.DEFAULT_MODEL)
        search_word['label'] = self.word['label']
        # Search word in database
        find_words = self.db.find(search_word)

        self.assertTrue(find_words[0]['type'] == change['type'])

    def test_remove_word(self):
        """Test well working of 'remove' function."""
        self.db.remove(self.word)

        # Creating a object to search
        search_word = dict(self.db.DEFAULT_MODEL)
        search_word['label'] = self.inserted_word_label
        # Search word in database
        find_words = self.db.find(search_word)

        self.assertTrue(find_words == [], 'Test if find a removed word')

    def test_auto_cleaning(self):
        """Test auto cleaning of database and update of 'settings' values"""
        labels = [
            'salut',
            'bonjour',
            'ca',
            'va',
            'bien',
            'oui'
        ]

        settings.LOCAL_DICT_MIN_COUNT = 6
        for label in labels:
            word = dict(self.db.DEFAULT_MODEL)
            word['label'] = label
            self.db.insert(word)

        self.db._clean_oldest()

        self.assertTrue(
            len(self.db) == settings.LOCAL_DICT_MIN_COUNT,
            'Test count of words'
        )

        # Creating a object to search
        search_word = dict(self.db.DEFAULT_MODEL)
        search_word['label'] = self.inserted_word_label
        # Search word in database
        find_words = self.db.find(search_word)

        self.assertTrue(find_words == [], 'Test if find a removed word')
