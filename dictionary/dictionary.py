from .storage import Table
from tinydb import Query
from .storagekit import _contains, _get_synonyms_on, _get_external_synonyms
from variables import Variables


class Dictionary:

    def __init__(self, dictionary_name='dictionary'):
        self.bdd = Table(dictionary_name)
        self.unknow_words = list()

    def __contains__(self, str_word):
        Word = Query()
        return self.bdd._db.contains(Word.label.test(_contains, str_word))

    def __getitem__(self, str_word):
        Word = Query()
        result = self.bdd._db.get(Word.label.test(_contains, str_word))

        if result is None:
            self.unknow_words.append(str_word)

        return result

    def __iter__(self):
        return iter(self.bdd.all())

    def __del__(self):
        if len(self.unknow_words) > 0:
            with open(Variables.UNKNOW_WORDS_PATH, 'w', encoding='utf-8', errors='ignore') as f:
                for uw in self.unknow_words:
                    f.write(uw)

    def lemmatize(self, sentence):
        pass

    def partOfSpeechTagging(self, sentence):
        pass

    def getSynonymsGroup(self, str_word):
        synonyms = list()
        external_synonyms = _get_external_synonyms(self.bdd, str_word)

        for s in external_synonyms:
            synonyms += _get_synonyms_on(self.bdd, s, str_word)
            synonyms += _get_synonyms_on(self.bdd, str_word, s)

        return list(dict.fromkeys(synonyms))
