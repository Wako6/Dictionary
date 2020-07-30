from tinydb import Query
# from tinydb import where
from dictionary import Dictionary, Unitex
from dictionary.storage import Table
from os import path


# d = Dictionary()
# print('faire' in d)
# print(d['avoir'])
# for word in d:
#     print('[' + str(word['ranking']) + '] ' + word['label'])
# print(d.getSynonymsGroup('jour'))

# with open('dela-fr-public.txt', encoding='utf-8', errors='ignore') as dela:
#     for line in dela.readlines():
#         if line != '\n':
#             print(line)

def parseDela():
    words = list()
    t = None
    _name = None
    _prev_name = path.join('unitex', 'name')
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
                _name = path.join('unitex', 'name')
            else:
                if word['label'][0].isalpha():
                    _name = path.join('unitex', word['label'][0])

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


# parseDela()

u = Unitex("unitex")
# print(u['buveuses de bière'])
# print(u.lemmatize('abaissées'))
# print(u.getType('abaissées'))
print(u.translateFlexionals(u.getFlexional('fais')))
print(u.translateSemantics(u.getSemantic('fais')))
