# -*- coding: utf-8 -*-
import scrapy
from ..items import Dictionaryv2Item


class LarousseSpider(scrapy.Spider):
    name = 'larousse'
    allowed_domains = ['www.larousse.fr/dictionnaires/francais']

    # Load a list of words and inject them as URLs
    def get_urls(filename):
        with open(filename) as infile:
            for word in infile:
                yield 'http://www.larousse.fr/dictionnaires/francais/' + word

    # start_urls = ['http://www.larousse.fr/dictionnaires/francais/faire/']
    start_urls = get_urls('mots.txt')

    def parse(self, response):
        word = dict()
        word['label'] = response.css('h2.AdresseDefinition::text').get()
        word['sens'] = []
        # Parse the response
        self.parseDefinitions(response, word)
        self.parseSynonyms(response, word)
        # Print all datas
        print()
        print(word['label'].upper())
        print("===================")
        for sens in word['sens']:
            print(sens['definition'])
            if 'synonyms' in sens: print('synonyms: ' + str(sens['synonyms']))
            if 'examples' in sens: print('examples: ' + str(sens['examples']))

        # items = Dictionaryv2Item()

        # items['definition'] = definition
        # items['synonyms'] = synonyms

        # yield items

    def parseDefinitions(self, response, word):
        definition_list = response.css('li.DivisionDefinition')

        for definition_block in definition_list:
            sens = LarousseSpider.create_new_sens()
            # Get list of sens block (information: definition + examples)
            definition_block = definition_block.css('::text').getall()
            # Clean datas
            while ' ' in definition_block: definition_block.remove(' ')

            step = 0
            sentence = str()
            sens['examples'] = []
            for info in definition_block:
                info = info.replace('\xa0', ' ').strip()
                # print(str(len(definition_block)) + ' : ' + info)
                sentence += ' ' + info
                # Step 1: Extract the complet definition of sens
                if step == 0 and info[-1] == ':':
                    # Remove first whitespace and (\xa0: ) at the end
                    definition = sentence[1:-2]
                    # print('definition: ' + definition)
                    sens['definition'] = definition
                    # Past to step 2 of extract and prepare for it
                    step += 1
                    sentence = ''
                    continue
                if len(definition_block) == 1:
                    sens['definition'] = info[:-1]
                    continue
                # Step 2 : Extract all example of sens
                if step == 1 and info[-1] in ('.', '?', '!'):
                    example = sentence.strip()
                    # print('example: ' + example)
                    sens['examples'].append(example)
                    sentence = ''

            # print(sens['definition'])
            # print(sens['examples'])
            word['sens'].append(sens)

    def parseSynonyms(self, response, word):
        def clear_str(string_list):
            # return s.replace(' - ', '')
            result = []
            for string in string_list:
                result += string.split(' - ')
            while '' in result: result.remove('')
            return result

        # Check if string start with substring
        def str_start_with(string, substring):
            for i, letter in enumerate(substring):
                if string[i] != letter:
                    return False
            return True

        sens_list = response.css('div.SensSynonymes')

        for sens in sens_list:
            # Get the sens definition
            definition = sens.css('p.DivisionDefinition::text, b::text').get()
            # Get sens synonyms
            synonyms_linked = sens.css('a.lienarticle::text').getall()
            synonyms_no_linked = sens.css('li.Synonyme::text').getall()
            # Clearing of datas
            synonyms_no_linked = clear_str(synonyms_no_linked)

            synonyms = synonyms_linked + synonyms_no_linked

            # print(definition)
            # print(synonyms)
            # Remove '.' and '...' at the end of synonyms definition
            if definition[-1] == '.':
                if definition[-2] == '.' and definition[-3] == '.':
                    definition = definition[:-3]
                else:
                    definition = definition[:-1]

            for sens in word['sens']:
                complet_definition = sens['definition']

                if str_start_with(complet_definition, definition):
                    sens['synonyms'] = synonyms
                    break
            else:
                nw_sens = LarousseSpider.create_new_sens()
                nw_sens['definition'] = definition
                nw_sens['synonyms'] = synonyms
                word['sens'].append(nw_sens)

    def create_new_sens():
        sens = dict()
        sens['definition'] = None
        sens['synonyms'] = []
        sens['examples'] = []
        return sens
