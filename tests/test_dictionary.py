import unittest
import os

from dictionary import Dictionary


class DictionaryTest(unittest.TestCase):
    """Test case used for test function of module 'dictionary'."""

    def setUp(self):
        """Initialization of test and insert a word."""
        self.dictionary = Dictionary(
            path='dicitionary-test'
        )
        self.name = self.dictionary.get_name()

    def tearDown(self):
        """Cleaning of resources used for tests."""
        path = self.dictionary._local_db.get_table_path()
        self.dictionary._local_db.close()
        del self.dictionary

        if self.name:
            os.remove(path)

    def test_init_dictionary(self):
        """Test if dictionary is correctly instanciate."""
        self.assertTrue(self.dictionary is not None)
        self.assertTrue(self.name)

    def test_find_word(self):
        """Test to find words in database."""
        results = self.dictionary.find(label='avoir')

        self.assertTrue(results != [], 'Test result of find function')

    def test_insert_word(self):
        """Test to insert a word in database."""
        label = 'test'
        self.dictionary.insert(label=label)

        self.assertTrue(label in self.dictionary, 'Test to find word')

    def test_find_one_word(self):
        """Test to find a word in database."""
        self.dictionary.insert(label='avoir')
        result = self.dictionary['avoir']

        self.assertTrue(result is not None, 'Test result of find function')

    def test_compose_word(self):
        """Test to compose a word"""
        inf_label = 'test'
        variants = {
            inf_label: ['masculin', 'singulier'],
            'teste': ['féminin', 'singulier'],
            'tests': ['masculin', 'pluriel'],
            'testes': ['féminin', 'pluriel']
        }

        for label, flex in variants.items():
            # Insert variants
            self.dictionary.insert(
                label=label,
                type='nom',
                lem=inf_label if label != inf_label else '',
                flexional=[flex]
            )

        results = self.dictionary.compose(lem=inf_label, flexional=['féminin'])
        # Test results size
        self.assertTrue(len(results) >= 2, 'Test if found at least 2 items')

        labels = [r['label'] for r in results]
        # Test if previous insertion exist in results
        self.assertTrue('teste' in labels, 'Test if \'teste\' is in result')
        self.assertTrue('testes' in labels, 'Test if \'testes\' is in result')

    def test_update_word(self):
        """Test if update of word infos working well."""
        word = self.dictionary.insert(
            label='test',
            semantic=['language courant']
        )
        # Change the type
        self.dictionary.update({
            'type': 'nom'
        }, word)

        self.assertTrue(word['type'] == 'nom', 'Test if type is changed')
        # Add a new semantic
        self.dictionary.update({
            'semantic': ['test']
        }, word, overwrite=False)

        self.assertTrue(
            'language courant' in word['semantic'],
            'Test if original semantic always exists'
        )
        self.assertTrue(
            'test' in word['semantic'],
            'Test if semantic is added'
        )

    def test_remove_word(self):
        """Test removing of a word in database."""
        pass

    def test_add_sens(self):
        """Test adding of sens in word infos."""
        word = self.dictionary.insert(
            label='test'
        )
        sens_count = len(word['sens'])

        self.dictionary.add_sens(word, 'When you try to do something.')

        self.assertTrue(
            len(word['sens']) == sens_count + 1,
            'Test if a sens is added'
        )

    def test_add_quote(self):
        """Test adding of quote in word infos."""
        word = self.dictionary.insert(
            label='test'
        )
        sens_count = len(word['quotes'])

        self.dictionary.add_quote(word, 'To test is to doubt')

        self.assertTrue(
            len(word['quotes']) == sens_count + 1,
            'Test if a sens is added'
        )

    def test_add_difficulty(self):
        """Test adding of difficulty in word infos."""
        word = self.dictionary.insert(
            label='test'
        )
        sens_count = len(word['difficulties'])

        self.dictionary.add_difficulty(
            word,
            'Usage',
            'A difficulty of test usage'
        )

        self.assertTrue(
            len(word['difficulties']) == sens_count + 1,
            'Test if a sens is added'
        )
