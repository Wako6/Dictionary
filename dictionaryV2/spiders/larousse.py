# -*- coding: utf-8 -*-
import scrapy
import re
# from ..items import Dictionaryv2Item
from dictionary.storage import Table
from tinydb import Query


i = 0
result_words = list()
memory_w = dict()
NB_WORDS = 181332


class LarousseSpider(scrapy.Spider):
    name = 'larousse'
    allowed_domains = ['http://www.larousse.fr']
    start_urls = [
            # 'http://www.larousse.fr/dictionnaires/francais/avoir/',
            # 'http://www.larousse.fr/dictionnaires/francais/etre/',
            # 'http://www.larousse.fr/dictionnaires/francais/faire/',
            # 'http://www.larousse.fr/dictionnaires/francais/confectionner/',
            # 'http://www.larousse.fr/dictionnaires/francais/apprêter/'
    ]
    WORDS = list()
    types = {}
    bdd = Table('dictionary')
    counter = 0

    def start_requests(self):
        while len(self.start_urls) > 0:
            yield scrapy.Request(url=self.start_urls.pop(), callback=self.parse)

    # Load a list of words and inject them as URLs
    def get_urls(filename):
        with open(filename) as infile:
            for word in infile.readlines():
                # if word not in LarousseSpider.WORDS:
                #     LarousseSpider.WORDS += word
                # else:
                #     continue
                yield 'http://www.larousse.fr/dictionnaires/francais/' + word

    # start_urls += list(get_urls('datas/documents/words_part_1.txt'))
    # start_urls += list(get_urls('datas/documents/words_part_2.txt'))
    # start_urls += list(get_urls('datas/documents/words_part_3.txt'))
    # start_urls += list(get_urls('datas/documents/words_part_4.txt'))
    start_urls += list(get_urls('..\\inf_words2.txt'))

    def parse(self, response):
        self.parsePage(response)

        # self.start_requests()
        # for url in self.start_urls:
        #     # print('[url] ' + url)
        #     url = response.urljoin(url)
        #     # yield scrapy.Request(url, callback=self.parsePage)
        #     yield response.follow(url, callback=self.parsePage)

    def parsePage(self, response):
        global i
        global result_words
        global memory_w
        global NB_WORDS
        word = dict()
        word['label'] = response.css('h2.AdresseDefinition::text').get()

        Word = Query()
        contain_word = self.bdd._db.contains(Word.label == word['label']) or word['label'] in memory_w
        if word['label'] is None or contain_word:
            # Trigger if an error occurs in the web content
            # error_file = open("error_words_searchv2.txt", "a")
            # error_file.write(self.current_search)
            # error_file.close()
            # print(self.current_search + ' failed !')
            return
        i += 1
        print('[' + str(i)[:3] + ' ' + str(i)[3:] + '/' + str(NB_WORDS) + '] ' + word['label'] + ' sucessed !')
        # word['ranking'] = i
        word['type'] = response.css('p.CatgramDefinition::text').get()
        word['sens'] = []

        # print()
        # print(word['label'].upper())
        # print(word['type'])
        # print("===================")

        # Parse the response
        for section in response.css('h1.TitrePage'):
            section_name = section.css('::text').get()
            if section_name == 'Définitions':
                self.parseDefinitions(response, word)
            # if section_name == 'Expressions':
            #     self.parseExpression(response, word)
                # Print
                # for expresion in word['expressions']:
                #     print(expresion['address'])
                #     if 'texts' in expresion: print('texts: ' + str(expresion['texts']))
            if section_name == 'Synonymes' or section_name == 'Synonymes et contraires':
                self.parseSynonyms(response, word)
                # Print
                # for sens in word['sens']:
                    # print(sens['definition'])
                    # if 'synonyms' in sens: print('synonyms: ' + str(sens['synonyms']))
                    # if 'examples' in sens: print('examples: ' + str(sens['examples']))
                    # self.addSearchWords(sens['synonyms'])
            if section_name == 'Homonymes':
                self.parseHomonyms(response, word)
                # Print
                # for homonym, catGramHomonym in word['homonyms']:
                #     print(homonym + ', ' + catGramHomonym)
            if section_name == 'Homonymes des variantes':
                self.parseHomonymsVar(response, word)
                # Print
                # for address, homonymsVar in word['homonymsVar']:
                #     print(address)
                #     for homonym, catGramHomonym in homonymsVar:
                #         print('   ' + homonym + ', ' + catGramHomonym)
            if section_name == 'Difficultés':
                self.parseDifficulties(response, word)
                # Print
                # for d_type, d_block in word['difficulties']:
                #     print(d_type)
                #     print(d_block)
            if section_name == 'Citations':
                self.parseQuotes(response, word)
                # for quote in word['quotes']:
                #     print(quote['author'] + quote['infosAuthor'])
                #     print(quote['text'])
                #     print(quote['infos'])
                #     print()

        # print(word)
        # print(json.dumps(word, indent=2))

        result_words.append(word)
        memory_w[word['label']] = None
        # self.bdd.insert(word)
        # yield {word['label']: word}

        if len(result_words) == 80:
            self.bdd._db.insert_multiple(result_words)
            result_words = list()
            memory_w = dict()

    def parseDefinitions(self, response, word):
        definition_list = response.css('li.DivisionDefinition')

        for definition_block in definition_list:
            sens = LarousseSpider._create_new_sens()
            definition_block_text = LarousseSpider._getText(definition_block.get())
            # definition_block_text = "Une phrase particulière : Il répondit:\"Je m'en vais ...\""
            definition_block = definition_block_text.split(':', 1)
            # Get the définition meaning
            _def = definition_block[0]
            _def = _def.split('.', 1)
            if '' in _def: _def.remove('')

            if len(_def) > 1:
                sens['tag'] = _def[0].strip()
                sens['definition'] = _def[1].strip()
            else:
                sens['definition'] = definition_block[0].strip()
            # If exist, get all examples
            if len(definition_block) > 1:
                sens['examples'] = LarousseSpider._splitSentences(definition_block[1])

            word['sens'].append(sens)

    def parseExpression(self, response, word):
        locutions = response.css('li.Locution')
        expresions = list()
        for locution in locutions:
            address = LarousseSpider._getText(locution.css('h2.AdresseLocution').get())
            texts = locution.css('span.TexteLocution')
            has_example = texts.css('span.ExempleDefinition').get() is not None

            # texts = texts.css('::text').get()
            texts = LarousseSpider._getText(texts.get())
            if has_example:
                texts = texts[:-2]
            texts = texts.replace('\xa0;', '').split(' ; ')
            address = address[:-2]

            locution = {'address': address, 'texts': texts}
            expresions.append(locution)

        word['expressions'] = expresions

    def parseSynonyms(self, response, word):
        sens_list = response.css('div.SensSynonymes')

        for sens in sens_list:
            # Get the sens definition
            definition = LarousseSpider._getText(sens.css('p.DivisionDefinition, b').get())
            synonyms = LarousseSpider._getText(sens.css('li.Synonyme').get())
            # Remove '.' and '...' at the end of synonyms definition
            if definition is None:
                word['sens'][0]['synonyms'] = synonyms
                return
            if definition[-1] == '.':
                if definition[-3] == '.':
                    definition = definition[:-3]
                else:
                    definition = definition[:-1]
            synonyms = synonyms.split(' - ')  # Split synonyms in list
            # Save the data
            for sens in word['sens']:
                if sens['definition'].startswith(definition):
                    sens['synonyms'] = synonyms
                    break
            else:
                nw_sens = LarousseSpider._create_new_sens()
                nw_sens['definition'] = definition
                nw_sens['synonyms'] = synonyms
                word['sens'].append(nw_sens)

    def parseHomonyms(self, response, word):
        homonym_list = response.css('ul.HomonymeDirects li.Homonyme')
        homonyms = list()

        for homonym in homonym_list:
            label = homonym.css('b::text').get()
            catGramHomonym = LarousseSpider._getText(homonym.css('span.CatGramHomonyme').get())

            homonyms.append((label, catGramHomonym))
        word['homonyms'] = homonyms

    def parseHomonymsVar(self, response, word):
        homonym_list = response.css('ul.VarianteHomonyme')
        homonyms = list()
        # li.Homonyme
        for homonym in homonym_list:
            address = homonym.css('p.AdresseHomonyme::text').get()
            homonymVar_list = homonym.css('li.Homonyme')
            homonymsVar = list()
            for homonymVar in homonymVar_list:
                label = homonymVar.css('b::text').get()
                catGramHomonym = LarousseSpider._getText(homonymVar.css('span.CatGramHomonyme').get())

                homonymsVar.append((label, catGramHomonym))
            homonyms.append((address, homonymsVar))
        word['homonymsVar'] = homonyms

    def parseDifficulties(self, response, word):
        difficulty_list = response.css('li.Difficulte')
        difficulties = list()

        for difficulty in difficulty_list:
            d_type = difficulty.css('p.TypeDifficulte::text').get()
            # FIXME - Need to parse ccorrectly some informations
            d_block = LarousseSpider._getText(difficulty.css('p.TypeDifficulte + *').get())
            difficulties.append((d_type, d_block))

        word['difficulties'] = difficulties

    def parseQuotes(self, response, word):
        quote_list = response.css('li.Citation')
        quotes = list()

        for quote in quote_list:
            author = LarousseSpider._getText(quote.css('span.AuteurCitation').get())
            infosAuthor = LarousseSpider._getText(quote.css('span.InfoAuteurCitation').get())
            text = LarousseSpider._getText(quote.css('span.TexteCitation').get())
            infos = LarousseSpider._getText(quote.css('span.InfoCitation').get())
            # FIXME - Missing some informations

            quote = {'author': author, 'infosAuthor': infosAuthor, 'text': text, 'infos': infos}
            quotes.append(quote)

        word['quotes'] = quotes

    @staticmethod
    def addUrl(url):
        LarousseSpider.start_urls.append(url)

    @staticmethod
    def addUrls(urls):
        if type(urls) is list:
            for url in urls:
                LarousseSpider.addUrl(LarousseSpider.allowed_domains[0] + url)

    # Create the structure of sens
    @staticmethod
    def _create_new_sens():
        sens = dict()
        sens['definition'] = None
        sens['synonyms'] = []
        sens['examples'] = []
        sens['tag'] = None
        return sens

    # Get all text in HTML code - TEMPORARILY
    @staticmethod
    def _getText(html_string):
        if html_string is None:
            return None

        result = re.sub(r'(<[^>]*>|&nbsp;|\xa0)', '', html_string)
        return result

    # Split basicaly sentences tanks to punctuation - TEMPORARILY
    @staticmethod
    def _splitSentences(text):
        # Define desired replacements here
        replacement = {
            '...': '&nsps;.',
            '.': '&npnt;.',
            '!': '&nxcm;.',
            '?': '&ntrg;.',
            '&nsps;': '...',
            '&npnt;': '.',
            '&nxcm;': '!',
            '&ntrg;': '?'
        }
        # Use these three lines to do the replacement
        subtitute = dict((re.escape(k), v) for k, v in replacement.items())
        pattern = re.compile("|".join(subtitute.keys()))
        _text = pattern.sub(lambda m: subtitute[re.escape(m.group(0))], text)
        # Split the setences and clean the result
        sentences = _text.split('.')
        while '' in sentences: sentences.remove('')
        # Put back the punstuation
        return [pattern.sub(lambda m: subtitute[re.escape(m.group(0))], s.strip()) for s in sentences]

    def removeTag(string):
        return re.sub(r'\([\s\S]+?\)', '', string)
