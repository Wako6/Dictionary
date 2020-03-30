from tinydb import Query


def _contains(x, str_word):
    if type(x) != list:
        return _compare_label(x, str_word)
    else:
        for e in x:
            if _compare_label(e, str_word):
                return True
        return False


def _compare_label(l1, l2):
    _l1 = l1.split(', ')
    _l2 = l2.split(', ')

    if len(_l1) > 1 and len(_l2) > 1:
        for _l in _l1:
            if _l in _l2:
                return True
    else:
        if len(_l1) > 1:
            return l2 in _l1
        elif len(_l2) > 1:
            return l1 in _l2
        else:
            return l1 == l2


def _get_synonyms_on(bdd, str_word, on_word):
    Word = Query()
    # Sens = Query()
    synonyms = list()

    def contains_synonym(sens, str_word):
        print(sens)
        return True

    # datas = bdd.find((Word.sens.test(contains_synonym, on_word)) & (Word.label == str_word))
    datas = bdd.find(Word.label == str_word)
    for word in datas:
        for sens in word['sens']:
            if on_word in sens['synonyms']:
                synonyms += sens['synonyms']
    return synonyms


def _get_external_synonyms(bdd, str_word, fields_name=['label']):
    Word = Query()
    Sens = Query()

    datas = bdd.find(Word.sens.any(Sens.synonyms.test(_contains, str_word)))
    return bdd.get_fields(datas, fields_name)
