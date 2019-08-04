'''
This module converts american measurements to russian.
Starting from temperature - Fahrenheit to Celsius
and finishing with cups/tsp/Tbsp to grams
'''

import re
import json


class ARConverter:

    def __init__(self):
        """
        - self.coefficients defines dictionary with key:value pairs as
        key = item (product), value - how many grams in 1 cup.
        Takes all values from coefficients.json file, which was made in make_constant_file.py
        module before initializing this class

        - self.ml_measures defines volume of different tools in ml
        """

        self.coefficients = dict()
        with open('coefficients.json', 'r') as coefficients:
            self.coefficients = json.load(coefficients)

        self.ml_measures = {'tbsp': 15, 'gallon': 3875.4, 'pint': 473, 'quart ': 946.4, 'cup': 240}

        self.units = [['cup', 'cups', 'c'], ['oz', 'ounce', 'ounces'], ['lb', 'pound', 'pounds'],
                      ['grams', 'gr', 'gram', 'g'], ['tsp', 'teaspoon'], ['tbsp', 'tablespoon', 'tablespoons'], ['gallon', 'gallons'],
                      ['pint', 'pints'], ['quart', 'quarts']]
        self.temperature_name = ['f', 'fahrenheit', 'fahrenheits']

    def process_line(self, line):
        """The main procedure - delete incorrect symbols, process the line, replace all measurements and
        returns converted result"""

        result = self.delete_incorrect_symbols(line)

        components = self.break_line(result)

        if len(components['amount'].keys()) > 0:
            for key in components['amount']:
                result = self.replace_in_line(result, key, components)

        return result

    def replace_in_line(self, line, amount, components):
        """Replaces amounts and measures in line"""


        result = line

        sub_dict = self.get_sub_dict_for_amount(amount, components)
        index = sub_dict['index']
        possible_fahrenheit = sub_dict.get('possible_F')
        measure = sub_dict.get('measure')

        if possible_fahrenheit and not measure:
            result = self.update_farenheits(result, sub_dict, index)
            return result





        if measure:

            if measure == 'cup':
                result = self.convert_cups_grams(line, sub_dict, index)

            elif measure == 'oz':
                result = self.convert_oz_grams(line, sub_dict, index)

            elif measure == 'lb':
                result = self.convert_lb_grams(line, sub_dict, index)

            elif measure in self.ml_measures.keys():
                result = self.convert_ml_gr(line, sub_dict, index)

            elif sub_dict.get('old_measure'):

                result = self.replace_words(result, sub_dict['old_measure'], sub_dict['measure'])
                result = self.replace_words(result, sub_dict['old_amount'], str(sub_dict['amount']), *index)

        self.update_index_after_replace(amount, components, sub_dict)


        return result

    def delete_incorrect_symbols(self, line):
        """Replace or delete special symbols from line. Such as ½ or °"""

        symbols_to_replace = {'½': '1/2', '¼': '1/4', '¾': '3/4', '°': ''}
        for key, value in symbols_to_replace.items():
            line = line.replace(key, value, 1)
        return line


    def break_line(self, line):
        """Divide line into amount, measure, item and another words in it"""

        result = {}

        numbers = self.find_and_check_numbers(line)
        result.update(numbers)

        words = self.find_words(line)
        result.update(words)

        return result

    def find_words(self, line):
        """"Find all words in a line, and check if there is an item"""

        result = {'item': '', 'words': ''}

        words = re.findall(r'[A-Za-z]+', line)
        for word in words:

            # Check if the word is an ingredient
            if word.lower() in self.coefficients:
                result.update({'item': word.lower()})

        result.update({'words': words})
        return result

    def find_and_check_numbers(self, line):
        """Find all numbers in a line and check words around them"""

        number_dict = {'amount': {}, 'measure': {}, 'old_measure': {},
                       'F_word': {}, 'possible_F': {}, 'index': {}}
        double_amounts = self.find_double_numbers(line)

        if len(double_amounts) == 0:
            self.check_for_single_amount(line, number_dict)

        else:
            self.handle_double_amount(line, number_dict)

        return number_dict

    def check_for_single_amount(self, line, number_dict):
        amounts = self.find_numbers(line)

        if len(amounts) > 0:
            for amount in amounts:
                amount = amount.strip()
                self.find_position(amount, line, number_dict)
                convert_amount = self.str_to_int_convert_amount(amount)

                number_dict['amount'].update({amount: convert_amount})

                self.check_possible_fahrenheit(amount, convert_amount, number_dict)
                self.look_around_number(line, amount, number_dict)

        return

    def handle_double_amount(self, line, number_dict):

        amounts = self.find_numbers(line)

        full_amount = None

        for amount in amounts:
            convert_amount = self.str_to_int_convert_amount(amount)

            number_dict['amount'].update({amount: convert_amount})

            self.find_position(amount, line, number_dict)

            self.check_possible_fahrenheit(amount, convert_amount, number_dict)
            self.look_around_number(line, amount, number_dict)

            if self.get_sub_dict_for_amount(amount, number_dict).get('measure'):
                full_amount = amount

        if full_amount:
            self.copy_sub_dict(full_amount, number_dict)

        return

    def find_position(self, word, line, number_dict, template=''):
        if template == '':
            template = word

        pre_positions = re.finditer(template, line)
        positions = [(pos.start(0), pos.end(0)) for pos in pre_positions]

        number_dict['index'].update({word: positions[0]})

        return

    def copy_sub_dict(self, full_amount, number_dict):
        for key in number_dict['amount']:
            measure_full_amount = number_dict['measure'].get(full_amount)
            old_measure_full_amount = number_dict['old_measure'].get(full_amount)
            number_dict['measure'].update({key: measure_full_amount})
            number_dict['old_measure'].update({key: old_measure_full_amount})

        return

    def find_double_numbers(self, line):
        """Find numbers which go in pairs ex: '4 to 5 cups of flour' """
        amounts = []
        n_p = '\d'

        split_words = ['to', '-']
        for s_word in split_words:
            amounts += re.findall(r'{}\s*{}\s*{}'.format(n_p, s_word, n_p), line)

        return amounts

    def find_numbers(self, line):
        """Find numbers using regexp"""

        amounts = re.findall(r'\d+[.,]\d+|\d+\s{1}[/\d]+|[/\d]+', line)

        return amounts

    def look_around_number(self, line, amount, number_dict):
        """Find words around number and check them further"""

        p_s = ['', '-']

        left_words = []
        right_words = []

        for symbol in p_s:

            left_pattern = r'\b[a-zA-Z][^\s]*\b[ {}]*(?=' + amount + ')'.format(symbol)
            # right_pattern = r'(?<=' + amount + ')[ {}]*[a-zA-Z]*'.format(symbol)
            right_pattern = r'(?<!\d)' + amount + '[ {}]*([a-zA-Z]+)'.format(symbol)

            left_word = re.findall(left_pattern, line)
            right_word = re.findall(right_pattern, line)

            # print(right_word, left_word)
            left_words += left_word
            right_words += right_word

        words = self.process_words_around_number(left_words + right_words, p_s)

        self.check_words_around_number(words, amount, number_dict)

        return words

    def process_words_around_number(self, words: list, symbols_for_delete: list):
        """Delete all excess symbols from words"""

        result = []
        for word in words:
            for symbol in symbols_for_delete:
                word = word.replace(symbol, '')

            word = word.strip()
            if word not in result:
                result.append(word)


        return result


    def check_words_around_number(self, words, amount, number_dict):
        """Check whether words around number are measure or Fahrenheit words"""

        # Check if a word is measure

        for word in words:
            word = word.strip()
            for i in range(len(self.units)):
                if word.lower() in self.units[i]:
                    measure = self.units[i][0]
                    number_dict['measure'].update({amount: measure})
                    number_dict['old_measure'].update({amount: word})

        # Check if word is Fahrenheit word
            if word.lower() in self.temperature_name:
                number_dict['F_word'].update({amount: word})
                number_dict['possible_F'].update({amount: True})

        return

    def cups_grams(self, item, cups, words):
        """Try to convert item from cups to grams if it is in self.coefficients
        dictionary. If everything went correct return new measure and TRUE flag.
        If item is not in dictionary - return input amount of cups and FALSE flag
        """

        item_in_coefficients = self.coefficients.get(item)

        if item_in_coefficients:
            grams = self.calculate_grams_if_item(item, cups, words)
            return [grams, True]
        else:
            print('INVALID PRODUCT: ', *words)
            return [cups, False]

    def calculate_grams_if_item(self, item, cups, words):
        """Check if the item could be 2 words name - Brown Sugar - if so it checks
        for the second word in [words] - and tries to find appropriate coefficient
        if it fail - it use {'': coefficient} in subdictionary.
        """

        if type(self.coefficients[item]) == dict:
            if len(words) > 0:
                for spec in words:
                    spec_in_dic = self.coefficients[item].get(spec)
                    if spec_in_dic:
                        grams = self.coefficients[item][spec] * cups
                        break
                    grams = self.coefficients[item][''] * cups
            else:
                grams = self.coefficients[item][''] * cups

        else:
            grams = self.coefficients[item] * cups

        return grams

    def update_farenheits(self, line, sub_dict, index: tuple):
        """Convert amount from F to C and replace Fahrenheit word in the line"""

        old_amount = sub_dict['amount']

        amount = self.fahrenheit_celsius(old_amount)
        result = self.replace_words(line, str(old_amount), str(amount), *index)

        is_F_word = sub_dict.get('F_word')

        if is_F_word:
            result = result.replace(sub_dict['F_word'], 'C')
        return result

    # High-level conversion functions

    def convert_cups_grams(self, line, sub_dict, index: tuple):
        """Converts cups to grams and process result whether the conversion is succeed or failed"""

        result = line
        cups_to_grams = self.cups_grams(sub_dict['item'], sub_dict['amount'], sub_dict['words'])

        if cups_to_grams[1]:  # if conversion is success
            result = self.replace_words(result, sub_dict['old_amount'], str(round(cups_to_grams[0])), *index)
            result = self.replace_words(result, sub_dict['old_measure'], 'grams')

            sub_dict.update({'amount': round(cups_to_grams[0])})

        return result

    def convert_ml_gr(self, line, sub_dict, index: tuple):
        """Calculates proportion for volume in self.ml_measures and converts cups to grams"""

        cups_in_measure = self.ml_cups(sub_dict['measure'])
        cups = sub_dict['amount']*cups_in_measure
        sub_dict.update({'amount': cups})

        result = self.convert_cups_grams(line, sub_dict, index)

        return result

    def convert_oz_grams(self, line, sub_dict, index: tuple):
        """Convert oz to grams and replace it in the line"""

        grams = self.oz_grams(sub_dict['amount'])
        result = self.replace_words(line, sub_dict['old_amount'], str(grams), *index)
        result = self.replace_words(result, sub_dict['old_measure'], 'grams')

        sub_dict.update({'amount': grams})

        return result

    def convert_lb_grams(self, line, sub_dict, index: tuple):
        """Convert lb to grams and replace it in the line"""

        old_amount = sub_dict['amount']
        grams = self.lb_grams(old_amount)
        result = self.replace_words(line, str(sub_dict['old_amount']), str(grams), *index)
        result = self.replace_words(result, sub_dict['old_measure'], 'grams')

        sub_dict.update({'amount': grams})

        return result

    # Simple one-line additional functions

    def fahrenheit_celsius(self, temperature):
        return round((temperature - 32)*5/9)

    def oz_grams(self, weight):
        return round(weight*28.35)

    def lb_grams(self, weight):
        return round(weight*453.6)

    def ml_cups(self, measure):
        """Calculates coefficient(proportion) for volume measures to cups"""

        result = self.ml_measures[measure]/self.ml_measures['cup']

        return result

    # Auxiliary functions
    def str_to_int_convert_amount(self, amount):
        ''' amount - is a string in format 1 3/4 or 1/2 - integer part
        divided from the fraction by space symbol
        If fraction part is incomplete ( /8) or (8/ ) it's ignored

        If some integer appears after fraction it's ignored
        If integer appears after integer - first integer ignored (in a case '1 16 oz can')
        '''


        string_numbers = amount.split()
        result = 0

        for i in range(len(string_numbers)):
            if '/' in string_numbers[i]:
                fraction_numbers = string_numbers[i].split('/')
                try:
                    result += round(int(fraction_numbers[0])/int(fraction_numbers[1]), 2)
                    return result
                except:
                    print('Error in fraction', string_numbers[i])
                    pass
            elif i > 0:                 # get rid of the previous part of double integer in a case '1 16 oz can'
                result = int(string_numbers[i])

            elif ',' in string_numbers[i] or '.' in string_numbers[i]:
                string_numbers[i] = string_numbers[i].replace(',', '.')
                result += float(string_numbers[i])

            else:
                result += int(string_numbers[i])
        return result

    def get_sub_dict_for_amount(self, amount, whole_dict):
        """Extract sub dictionary for the particular amount as a key value in all sub dictionaries
        For example, we have such a dictionary {'amount': {'1 1/2': 1.5, '350': 350}, 'measure': {'1 1/2': 'cup'},
                                                                                        'F_word':{'350': 'F'}}
        for amount = '1 1/2' this function extract dictionary {'old_amount': '1 1/2', 'amount': 1.5, 'measure': 'cup'}
        for amount = '350' it should be {'old_amount': 350, 'amount': 350, 'F_word': 'F'}

        """

        result = {}
        for key in whole_dict:
            try:
                am_in_keys = whole_dict[key].get(amount)
                if am_in_keys != None:
                    result.update({'old_amount': amount})
                    result.update({key: whole_dict[key][amount]})

            except AttributeError:
                result.update({key: whole_dict[key]})

        return result

    def check_possible_fahrenheit(self, amount, convert_amount, number_dict):
        if convert_amount > 250:
            number_dict['possible_F'].update({amount: True})
        else:
            number_dict['possible_F'].update({amount: False})
            return

    def replace_words(self, line, what, to_what, start=0, end=None):

        if start == 0 and end == None:
            result = line.replace(what, to_what)
        else:
            result = line[:start] + line[start:end].replace(what, to_what) + line[end:]

        return result

    def update_index_after_replace(self, amount, components, sub_dict):
        amounts = [key for key in components['amount'].keys()]
        amount_index = amounts.index(str(amount))

        old_amount_len = len(sub_dict['old_amount'])
        new_amount_len = len(str(sub_dict['amount']))

        if amount_index < len(amounts)-1:
            for key in amounts[amount_index+1::]:
                old_index = components['index'].get(key)
                new_index_start = old_index[0] - old_amount_len + new_amount_len
                new_index_end = old_index[1] - old_amount_len + new_amount_len
                new_index = (new_index_start, new_index_end)
                components['index'].update({key: new_index})

        pass

