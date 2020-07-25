from .storage import Table
from tinydb import Query
from .storagekit import _contains, _get_synonyms_on, _get_external_synonyms


class Dictionary:

    def __init__(self, dictionary_name='dictionary'):
        self.bdd = Table(dictionary_name)

    def __contains__(self, str_word):
        Word = Query()
        return self.bdd._db.contains(Word.label.test(_contains, str_word))

    def __getitem__(self, str_word):
        Word = Query()
        return self.bdd.find(Word.label.test(_contains, str_word))

    def __iter__(self):
        Word = Query()
        return iter(self.bdd.find(Word))

    def lemmatize(self, sentence):
        pass

    def partOfSpeechTagging(self, sentence):
        pass

    def getSynonymsGroup(self, str_word):
        synonyms = list()
        external_synonyms = _get_external_synonyms(self.bdd, str_word)

        for s in external_synonyms:
            # print(s)
            synonyms += _get_synonyms_on(self.bdd, s, str_word)
            synonyms += _get_synonyms_on(self.bdd, str_word, s)

        return list(dict.fromkeys(synonyms))
