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
        """The main procedure, handles with lines and returns converted result"""

        components = self.break_line(line)
        result = line

        if len(components['amount'].keys()) > 0:
            for key in components['amount']:
                sub_dict = self.get_sub_dict_for_amount(key, components)

                possible_fahrenheit = sub_dict.get('possible_F')

                if possible_fahrenheit:
                    result = self.update_farenheits(line, sub_dict)
                    continue

                is_measure = sub_dict.get('measure')

                if is_measure:
                    measure = sub_dict['measure']

                    if measure == 'cup':
                        result = self.convert_cups_grams(line, sub_dict)

                    elif measure == 'oz':
                        result = self.convert_oz_grams(line, sub_dict)

                    elif measure == 'lb':
                        result = self.convert_lb_grams(line, sub_dict)

                    elif measure in self.ml_measures.keys():
                        result = self.convert_ml_gr(line, sub_dict)

                elif sub_dict.get('old_measure'):
                    result = line.replace(sub_dict['old_measure'], sub_dict['measure'])
                    # result = result.replace(sub_dict['old_amount'], str(sub_dict['amount']))

        return result

    def break_line(self, line):
        """Divide line into amount, measure, item and another words in it"""

        result = {}

        numbers = self.find_numbers(line)
        result.update(numbers)

        words = self.find_words(line)
        result.update(words)

        return result

    def find_words(self, line):
        result = {'item': '', 'words': ''}

        words = re.findall(r'[A-Za-z]+', line)
        for word in words:

            # Check if the word is an ingredient
            if word in self.coefficients:
                result.update({'item': word})

        result.update({'words': words})
        return result

    def find_numbers(self, line):
        number_dic = {'amount': {}, 'measure': {}, 'old_measure': {}, 'F_word': {}, 'possible_F': {}}

        amounts = re.findall(r'\d+[.,]\d+|\d+\s{1}[/\d]+|[/\d]+', line)

        if len(amounts) > 0:
            for amount in amounts:
                amount = amount.strip()
                convert_amount = self.str_to_int_convert_amount(amount)
                number_dic['amount'].update({amount: convert_amount})

                if convert_amount > 250:
                    number_dic['possible_F'].update({amount: True})
                else:
                    number_dic['possible_F'].update({amount: False})

                self.look_around_number(line, amount, number_dic)

        return number_dic

    def look_around_number(self, line, amount, number_dic):

        left_pattern = r'\b[a-zA-Z][^\s]*\b\s*(?=' + amount + ')'
        right_pattern = r'(?<=' + amount + ')\\s*[a-zA-Z]*'
        left_word = re.findall(left_pattern, line)
        right_word = re.findall(right_pattern, line)

        self.check_words_around_number(right_word, amount, number_dic)
        self.check_words_around_number(left_word, amount, number_dic)

        return

    def check_words_around_number(self, words, amount, number_dic):
        # Check if a word is measure

        for word in words:
            word = word.strip()
            for i in range(len(self.units)):
                if word.lower() in self.units[i]:
                    measure = self.units[i][0]
                    number_dic['measure'].update({amount: measure})
                    number_dic['old_measure'].update({amount: word})

        # Check if word is Fahrenheit word
            if word.lower() in self.temperature_name:
                number_dic['F_word'].update({amount: word})
                number_dic['possible_F'].update({amount: True})

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

    def update_farenheits(self, line, sub_dict):
        old_amount = sub_dict['amount']

        amount = self.fahrenheit_celsius(old_amount)
        result = line.replace(str(old_amount), str(amount))

        is_F_word = sub_dict.get('F_word')

        if is_F_word:
            result = result.replace(sub_dict['F_word'], 'C')

        return result

    # High-level conversion functions

    def convert_cups_grams(self, line, components):
        """Converts cups to grams and process result whether the conversion is succeed or failed"""

        cups_to_grams = self.cups_grams(components['item'], components['amount'], components['words'])
        if cups_to_grams[1]:  # if conversion is success
            result = line.replace(components['old_amount'], str(round(cups_to_grams[0])) + ' ')
            result = result.replace(components['old_measure'], 'grams')

        else:
            result = line
        return result

    def convert_ml_gr(self, line, components):
        """Calculates proportion for volume in self.ml_measures and converts cups to grams"""

        cups_in_measure = self.ml_cups(components['measure'])
        components.update({'amount': components['amount']*cups_in_measure})
        result = self.convert_cups_grams(line, components)

        return result

    def convert_oz_grams(self, line, components):
        grams = self.oz_grams(components['amount'])
        result = line.replace(components['old_amount'], str(grams))
        result = result.replace(components['old_measure'], 'grams')

        return result

    def convert_lb_grams(self, line, components):
        old_amount = components['amount']
        grams = self.lb_grams(old_amount)
        result = line.replace(str(components['old_amount']), str(grams))
        result = result.replace(components['old_measure'], 'grams')

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
            elif i > 0:
                result = int(string_numbers[i])

            elif ',' in string_numbers[i] or '.' in string_numbers[i]:
                string_numbers[i] = string_numbers[i].replace(',', '.')
                result += float(string_numbers[i])

            else:
                result += int(string_numbers[i])
        return result

    def get_sub_dict_for_amount(self, amount, whole_dict):
        result = {}
        for key in whole_dict:
            try:
                am_in_keys = whole_dict[key].get(amount)
                if am_in_keys:
                    result.update({'old_amount': amount})
                    result.update({key: whole_dict[key][amount]})
            except AttributeError:
                result.update({key: whole_dict[key]})

        return result


