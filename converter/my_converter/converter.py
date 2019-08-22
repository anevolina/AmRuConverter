'''
This module converts american measurements to russian.
Starting from temperature - Fahrenheit to Celsius
and finishing with cups/tsp/Tbsp to grams
'''

import re
import json
import os.path
import demoji


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
        file_dir = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(file_dir, 'coefficients.json'), 'r') as coefficients:
            self.coefficients = json.load(coefficients)

        self.ml_measures = {'tbsp': 15, 'gallon': 3875.4, 'pint': 473, 'quart ': 946.4, 'cup': 240, 'stick': 120}

        self.units = [['cup', 'cups', 'c'], ['oz', 'ounce', 'ounces'], ['lb', 'lbs', 'pound', 'pounds'],
                      ['grams', 'gr', 'gram', 'g'], ['tsp', 'teaspoon'], ['tbsp', 'tablespoon', 'tablespoons'], ['gallon', 'gallons'],
                      ['pint', 'pints'], ['quart', 'quarts'], ['stick', 'sticks'], ['ml', 'milliliters', 'milliliter'],
                      ['inch', 'inches', 'in', "''"]]
        self.fahrenheit_names = ['f', 'fahrenheit', 'fahrenheits']
        self.celsius_names = ['c', 'celsius']
        demoji.download_codes()


    def process_line(self, line):
        """The main procedure - delete incorrect symbols, process the line, replace all measurements and
        returns converted result"""

        result = self.delete_incorrect_symbols(line)

        is_link_templ = 'https|www|\.com'
        is_link = re.findall(is_link_templ, result)

        if is_link:
            return result

        components = self.break_line(result)

        if len(components['amount'].keys()) > 0:
            for key in components['amount']:
                result = self.replace_in_line(result, key, components)
        return result

    def replace_in_line(self, line, amount, components):
        """Replaces amounts and measures in line"""

        result = line

        sub_dict = self.get_sub_dict_for_amount(amount, components)
        amount_index = sub_dict.get('index')
        measure_index = sub_dict.get('index_m')
        measure = sub_dict.get('measure')
        possible_fahrenheit = sub_dict.get('possible_F')
        all_indexes = components.get('index')

        if possible_fahrenheit:

            old_measure = sub_dict.get('old_measure')
            if old_measure in ['c', 'C']:
                result = self.update_farenheits(result, sub_dict, all_indexes, warning=True)

            if not measure:
                result = self.update_farenheits(result, sub_dict, all_indexes)

            return result

        if measure:

            if measure == 'cup':
                result = self.convert_cups_grams(result, sub_dict, all_indexes)

            elif measure == 'oz':
                result = self.convert_oz_grams(result, sub_dict, all_indexes)

            elif measure == 'lb':
                result = self.convert_lb_grams(result, sub_dict, all_indexes)

            elif measure in self.ml_measures.keys():

                result = self.convert_ml_gr(result, sub_dict, all_indexes)

            elif measure == 'inch':
                result = self.convert_inches_cm(result, sub_dict, all_indexes)

            elif sub_dict.get('old_measure'):

                result = self.replace_words(result, sub_dict['old_amount'], str(sub_dict['amount']), all_indexes, amount_index)

                result = self.replace_words(result, sub_dict['old_measure'], sub_dict['measure'], all_indexes, measure_index)


        possible_inch = components.get('possible_inch')
        if possible_inch and not measure:
            result = self.inch_warning(result, possible_inch)

        return result

    def delete_incorrect_symbols(self, line):
        """Replace or delete special symbols from line. Such as ½ or °"""

        symbols_to_replace = {'⅛': '1/8', '½': '1/2', '⅓': '1/3', '¼': '1/4', '⅔': '2/3', '¾': '3/4', '°': '', '″': 'inch',
                              "''": 'inch', '×': 'x'}
        for key, value in symbols_to_replace.items():
            line = line.replace(key, ' ' + value).strip()
        line = self.deEmojify(line)

        return line

    def deEmojify(self, line):
        line = demoji.replace(line)

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
                       'possible_F': {}, 'index': {}, 'possible_inch':{}}
        double_amounts = self.find_double_numbers(line, number_dict)

        self.check_for_single_amount(line, number_dict)

        if len(double_amounts) > 0:
            self.handle_double_amount(number_dict, double_amounts)

        return number_dict

    def check_for_single_amount(self, line, number_dict):
        """Handles lines with amounts in one number (not '4-5 cups', just '4 cups' )"""

        amounts = self.find_numbers(line)

        if len(amounts) > 0:
            for amount in amounts:
                amount = amount.strip()
                template = '(?<!\d){}(?![/.-])'.format(amount)
                self.find_position(amount, line, number_dict, template)
                convert_amount = self.str_to_int_convert_amount(amount)

                number_dict['amount'].update({amount: convert_amount})

                self.check_possible_fahrenheit(amount, convert_amount, number_dict)
                self.look_around_number(line, amount, number_dict)


        return

    def handle_double_amount(self, number_dict, double_amounts):
        """Handles lines with amounts in two numbers ('4-5 cups', '4 to 5 cups' )"""
        amounts = []
        for d_amount in double_amounts:
            amounts += self.find_numbers(d_amount)

        for amount in amounts:
            amount = amount.strip()

            if self.get_sub_dict_for_amount(amount, number_dict).get('measure'):
                self.copy_sub_dict(amount, amounts, number_dict)

        return

    def find_position(self, word, line, number_dict, template='', simple=False):
        """Find position for word in a line. With variable template if needed"""


        if template == '':
            template = word

        pre_positions = re.finditer(template, line)
        try:
            positions = [(pos.start(0), pos.end(0)) for pos in pre_positions]
            if simple:
                return positions
            number_dict['index'].update({word: positions})
        except:
            if simple:
                return (0, len((line)))
            number_dict['index'].update({word: (0, len(line))})
        return

    def copy_sub_dict(self, full_amount, amounts, number_dict):
        """Copy sub dictionary from one amount to another - used in case when we have amount with 2 numbers
        for ex. '4 - 5 cups'  here we have to convert amounts for '4 cups' and for '5 cups'
        """

        for key in number_dict['amount']:
            if key in amounts:
                measure_full_amount = number_dict['measure'].get(full_amount)
                old_measure_full_amount = number_dict['old_measure'].get(full_amount)
                number_dict['measure'].update({key: measure_full_amount})
                number_dict['old_measure'].update({key: old_measure_full_amount})

        return

    def find_double_numbers(self, line, number_dict):
        """Find numbers which go in pairs ex: '4 to 5 cups of flour' """

        amounts = self.find_numbers(line)
        d_amounts = []

        if len(amounts) >= 2:
            split_words = ['to', '-', 'x']
            for s_word in split_words:
                for i in range(len(amounts)-1):
                    d_amount = re.findall(r'{}\s*{}\s*{}'.format(amounts[i], s_word, amounts[i+1]), line)
                    d_amounts += d_amount
                    if s_word == 'x' and len(d_amount) > 0:
                        number_dict['possible_inch'].update({d_amount[0]: True})
        return d_amounts

    def find_numbers(self, line, templates=None):
        """Find numbers using regexp"""
        templates = templates or ['\d+[.,]\d+|\d*[ ]*\d+[/]\d+|\d+']

        for template in templates:
            amounts = re.findall(r'{}'.format(template), line)

            if len(amounts) > 0:
                return amounts

        return []

    def look_around_number(self, line, amount, number_dict):
        """Find words around number and check them further"""

        p_s = ['', '-']

        left_words = []
        right_words = []

        for symbol in p_s:

            left_pattern = r'\b[a-zA-Z][^\s]*\b[ {}]*(?=' + amount + ')'.format(symbol)
            right_pattern = r'(?<!\d)' + amount + '[ {}]*([a-zA-Z]+)'.format(symbol)

            left_word = re.findall(left_pattern, line)
            right_word = re.findall(right_pattern, line)

            left_words += left_word
            right_words += right_word

        words = self.process_words_around_number(left_words + right_words, p_s)

        self.check_words_around_number(words, amount, number_dict, line)

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

    def check_words_around_number(self, words, amount, number_dict, line):
        """Check whether words around number are measure or Fahrenheit words"""

        # Check if a word is measure

        for word in words:
            word = word.strip()
            for i in range(len(self.units)):
                if word.lower() in self.units[i]:
                    measure = self.units[i][0]
                    number_dict['measure'].update({amount: measure})
                    number_dict['old_measure'].update({amount: word})
                    template = r'[ \d-]{}[ \d-]*|[ \d-]*{}[ \d-]'.format(word, word)
                    self.find_position(word, line, number_dict, template)


        # Check if word is Fahrenheit word
            if word.lower() in self.fahrenheit_names:
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


    def update_farenheits(self, line, sub_dict, all_indexes, warning=False):
        """Convert amount from F to C and replace Fahrenheit word in the line"""
        words = sub_dict.get('words')
        old_amount = sub_dict['amount']
        index = sub_dict['index']

        amount = self.fahrenheit_celsius(old_amount)
        result = self.replace_words(line, str(old_amount), str(amount), all_indexes, index)

        for word in words:
            if word.lower() in self.fahrenheit_names:
                template = '[ \d-]{}[ ]'.format(word)
                index = self.find_position(word, line, sub_dict, template, simple=True)
                result = self.replace_words(result, word, 'Celsius', all_indexes, index)

            if word.lower() in self.celsius_names:
                warning = True

        if warning:
            key = '(Possible mistake! {} - too much to be in Celsius. {}F = {}C)'.format(old_amount, old_amount, amount)
            result = line + ' ' + key

        return result

    def inch_warning(self, line, possible_inches):
        converted = []

        for key in possible_inches:
            if possible_inches[key]:
                a = self.find_numbers(key)
                assert len(a) == 2, 'wrong amount: {}'.format(key)
                a[0], a[1] = self.str_to_int_convert_amount(a[0]), self.str_to_int_convert_amount(a[1])
                a.append(self.in_cm(a[0]))
                a.append(self.in_cm(a[1]))
                converted.append('{} x {} inches = {} x {} cm'.format(a[0], a[1], a[2], a[3]))
                possible_inches.update({key: False})

        if len(converted) == 0:
            return line

        result = line + ' (Measures might be in inches: ' + ','.join(converted) + ')'

        return result

    # High-level conversion functions

    def convert_cups_grams(self, line, sub_dict, all_indexes):
        """Converts cups to grams and process result whether the conversion is succeed or failed"""

        result = line
        index = sub_dict['index']
        index_m = sub_dict['index_m']

        old_amount = sub_dict['old_amount']

        cups_to_grams = self.cups_grams(sub_dict['item'], sub_dict['amount'], sub_dict['words'])
        new_amount = str(round(cups_to_grams[0]))

        if cups_to_grams[1]:  # if conversion is success
            result = self.replace_words(result, old_amount, new_amount, all_indexes, index)

            result = self.replace_words(result, sub_dict['old_measure'], 'grams', all_indexes, index_m)

        return result

    def convert_ml_gr(self, line, sub_dict, all_indexes):
        """Calculates proportion for volume in self.ml_measures and converts cups to grams"""

        cups_in_measure = self.ml_cups(sub_dict['measure'])
        cups = sub_dict['amount']*cups_in_measure
        sub_dict.update({'amount': cups})

        result = self.convert_cups_grams(line, sub_dict, all_indexes)

        return result

    def convert_oz_grams(self, line, sub_dict, all_indexes):
        """Convert oz to grams and replace it in the line"""

        index = sub_dict.get('index')
        index_m = sub_dict.get('index_m')

        grams = self.oz_grams(sub_dict['amount'])
        result = self.replace_words(line, sub_dict['old_amount'], str(grams), all_indexes, index)

        result = self.replace_words(result, sub_dict['old_measure'], 'grams', all_indexes, index_m)

        return result

    def convert_lb_grams(self, line, sub_dict, all_indexes):
        """Convert lb to grams and replace it in the line"""

        index = sub_dict.get('index')
        index_m = sub_dict.get('index_m')

        grams = self.lb_grams(sub_dict['amount'])
        result = self.replace_words(line, str(sub_dict['old_amount']), str(grams), all_indexes, index)

        result = self.replace_words(result, sub_dict['old_measure'], 'grams', all_indexes, index_m)

        return result

    def convert_inches_cm(self, line, sub_dict, all_indexes):

        index = sub_dict.get('index')
        index_m = sub_dict.get('index_m')

        cm = self.in_cm(sub_dict['amount'])
        result = self.replace_words(line, str(sub_dict['old_amount']), str(cm), all_indexes, index)
        result = self.replace_words(result, sub_dict['old_measure'], 'cm', all_indexes, index_m)

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

    def in_cm(self, inches):
        """Calculates centimeters from inches"""
        return round(inches*2.54)

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
                    measure = whole_dict['old_measure'].get(amount)
                    if measure:
                        result.update({'index_m': whole_dict['index'].get(measure)})

            except AttributeError:
                result.update({key: whole_dict[key]})

        return result

    def check_possible_fahrenheit(self, amount, convert_amount, number_dict):
        """We consider a number as a possible fahrenheit if it's larger than 270 (because recipes with this temperature
        are quite rare)"""

        if convert_amount > 270:
            number_dict['possible_F'].update({amount: True})
        else:
            number_dict['possible_F'].update({amount: False})
            return

    def replace_words(self, line, what, to_what, all_indexes, args=None):
        """Replace words in line in respect with start and end positions for searching"""
        if type(args) == tuple:
            start = args[0]
            end = args[1]

        elif type(args) == list and len(args) > 0:
        #Remove indexes from used args, in case there are more than 1 arg with the same value

            first = args[0]
            args.remove(first)
            start = first[0]
            end = first[1]

        else:
            result = line.replace(what, to_what)
            return result

        result = line[:start] + line[start:end].replace(what, to_what) + line[end:]
        self.update_all_indexes_after_replacement(what, to_what, start, end, all_indexes)

        return result

    def update_all_indexes_after_replacement(self, old, new, start, end, all_indexes):
        """Updates all indexes for a line"""

        for key in all_indexes:
            for value in all_indexes[key]:
                if value[0] >= start and value[1] > end:
                    v_index = all_indexes[key].index(value)
                    new_index = self.get_new_index(old, new, value)
                    all_indexes[key][v_index] = new_index
        pass

    def get_new_index(self, old, new, index):
        """Updates particular given index as a tuple"""

        shift = len(str(new)) - len(str(old))
        new_index = index[0] + shift, index[1] + shift

        return new_index
