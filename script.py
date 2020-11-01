# -*- coding: UTF-8 -*-

from tinydb import Query
# from tinydb import where
from dictionary import Unitex, Dictionary
from dictionary.storage import Table
import os
from dictionary.tools import _contains
from variables import Variables


def parseDela():
    words = list()
    t = None
    _name = None
    _prev_name = os.path.join('unitex', 'name')
    # _i = 0
    with open('dela-fr-public.dic', encoding='utf-8', errors='ignore') as fp:
        line = fp.readline()
        cnt = 1
        while line:
            word = dict()
            # print("Line {}: {}".format(cnt, line.strip()))
            line = line.split(',', 1)
            word['label'] = line[0].replace('\\', '')
            line = line[1].split('.')
            word['lem'] = line[0].replace('\\', '')
            word['tags'] = line[1].strip()
            line = word['tags'].split(':')
            word['flexional'] = line[1:]
            line = line[0].split('+')
            word['gram'] = line[0]
            word['semantic'] = line[1:]

            if cnt >= 1000:
                _cnt = str(cnt)[:-3] + ' ' + str(cnt)[-3:]
            else: 
                _cnt = str(cnt)
            print("[{}/792 260]: {},{}.{}[{}]{}{}".format(_cnt, word['label'], word['lem'].upper(), word['tags'], word['gram'], word['semantic'], word['flexional']))
            # t.insert(word)
            line = fp.readline()
            cnt += 1

            # _i += 1
            if word['label'][0] == word['label'][0].upper():
                _name = os.path.join('unitex', 'name')
            else:
                if word['label'][0].isalpha():
                    _name = os.path.join('unitex', word['label'][0])

            if _prev_name == _name:
                words.append(word)
                continue
            else:
                t = Table(_prev_name)
                _prev_name = _name
                # print(_name + ': ' + str(_i))
                # _i = 0
                t._db.insert_multiple(words)
                words = list()
                words.append(word)

            # t.insert(word)


if __name__ == '__main__':
    # For test Dictionary Class
    #
    d = Dictionary()
    result = d.compose(
        'avoir',
        gram='verbe',
        sem=['langage courant'],
        flex=['1st personne']

    )

    print([r['label'] for r in result])
    print('\n')

    # print('véhicule' in d)
    # print(d['préparer'])
    # for word in d:
    #     print(word['label'])

    # print(d.fetch('avoir'))

    # group = d.getSynonymsGroup('recouvrir')
    # print(group)
    # for word in group:
    #     print(word)
    #     _g = d.getSynonymsGroup(word)
    #     print("Same group: {}".format(_g == group))
    #     print(_g)

    # For parse Unitex dictionary from Dela
    #
    # parseDela()

    # For test Unitex Class
    #
    u = Unitex("unitex")
    # print(u.lemmatize('Prépare'))

    # print(u['buveuses de bière'])
    # print(u.lemmatize('abaissées'))
    # print(u.getType('abaissées'))
    # print(u.translateFlexionals(u.getFlexional('fais')))
    # print(u.translateSemantics(u.getSemantic('fais')))
    # print(u.compose('faire', 'V', flex=['P3s']))

    # For extract infinitive words from unitex database
    #
    # Word = Query()
    # res = u.search(Word.lem == '', 'datas')
    # with open('inf_words.txt', 'r', encoding='utf-8', errors='ignore') as fi:
    #     with open('inf_words2.txt', 'w', encoding='utf-8', errors='ignore') as f2:
    #         for word in fi.readlines():
    #             if word not in d:
    #                 print(word)
    #                 f2.write(word)

    # bdd = Table('dictionary')
    # word = Query()

    # print(bdd._db.search(word.label.test(_contains, 'abrogatif')))
    # print(bdd.find(word.label == 'abrogatif, abrogative'))

    # ===================================================================

    def data_treatment(filename, memory=list()):
        file_path = os.path.join('datas', 'documents', filename)
        abs_file_path = os.path.join(Variables.PROJECT_PATH, file_path)
        lines = None

        with open(abs_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.strip('\n').strip() for line in f.readlines()]

        with open(abs_file_path, 'w', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(lines):
                # print('[{}/{}] {}'.format(i + 1, len(lines), line))
                # Here treatment to do
                lem = None
                for _lem in u.lemmatize(line):
                    if not _lem:
                        continue
                    _lem, _type = _lem
                    if lem:
                        if _type == 'V' and lem[1] != 'V':
                            continue
                        elif _type == 'N' and lem[1] not in ['V', 'N']:
                            continue

                    lem = _lem, _type

                lem = lem[0] if lem else line
                print('[{}/{}] {} -> {}'.format(i + 1, len(lines), line, lem))

                if lem != '' and lem not in memory:
                    memory.append(lem)
                    f.write('{}\n'.format(lem))

    # tmp = list()
    # for i in range(4):
    #     print('FILE {}'.format(i + 1))
    #     data_treatment('words_part_{}.txt'.format(i + 1), tmp)
