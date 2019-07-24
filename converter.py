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
                      ['grams', 'gr', 'gram'], ['tsp', 'teaspoon'], ['tbsp', 'tablespoon'], ['gallon', 'gallons'],
                      ['pint', 'pints'], ['quart', 'quarts']]
        self.temperature_name = ['f', 'fahrenheit', 'fahrenheits']

    def process_line(self, line):
        """The main procedure, handles with lines and returns converted result"""

        components = self.break_line(line)

        item = components['item']
        measure = components['measure']
        amount = components['amount']
        around_words = components['words']
        fahrenheit = components['F']

        if fahrenheit or amount > 250:
            amount = self.fahrenheit_celsius(amount)

        if measure == 'cup':
            result = self.convert_cups_grams(item, amount, around_words)

        elif measure == 'oz':
            result = self.convert_oz_grams(item, amount, around_words)

        elif measure == 'lb':
            result = self.convert_lb_grams(item, amount, around_words)

        elif measure in self.ml_measures.keys():
            result = self.convert_ml_gr(item, amount, measure, around_words)

        else:
            result = self.concatenate_result(amount, measure, item, *around_words)

        return result

    def break_line(self, line):
        """Divide line into amount, measure, item and another words in it"""

        result = {}

        amount = self.find_numbers(line)
        result.update({'amount': amount})

        words = self.find_words(line, amount)
        result.update(words)

        return result

    def find_words(self, line, amount):
        result = {'measure': '', 'item': '', 'words': '', 'F': False}
        words_to_delete = []

        words = re.findall(r'[A-Za-z]+', line)
        for word in words:

            # Check if a word is measure
            for i in range(len(self.units)):
                if word.lower() in self.units[i]:
                    measure = self.units[i][0]
                    words_to_delete.append(word)
                    result.update({'measure': measure})
                    break

            # Check if the word is an ingredient
            if word in self.coefficients:
                result.update({'item': word})
                # words_to_delete.append(word)

            # Check if we have to convert F to C
            if word.lower() in self.temperature_name and amount > 100:
                words_to_delete.append(word)
                result.update({'F': True})
                words.append('celsius')

        for word in words_to_delete:
            words.remove(word)

        result.update({'words': words})

        return result

    def find_numbers(self, line):
        amount = re.findall(r'\d[\d /]+', line)
        if len(amount) > 0:
            amount = self.str_to_int_convert_amount(amount[0])
            return amount
        return 0

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
            print('INVALID PRODUCT: ', item)
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

    # High-level conversion functions

    def convert_cups_grams(self, item, amount, around_words, measure='cup'):
        """Converts cups to grams and process result whether the conversion is succeed or failed"""

        cups_to_grams = self.cups_grams(item, amount, around_words)

        if cups_to_grams[1]:  # if conversion is success
            result = self.concatenate_result(round(cups_to_grams[0]), 'grams', item, *around_words)
        else:
            result = self.concatenate_result(amount, measure, item, *around_words)
        return result

    def convert_ml_gr(self, item, amount, measure, around_words):
        """Calculates proportion for volume in self.ml_measures and converts cups to grams"""

        cups_in_measure = self.ml_cups(measure)
        amount = amount * cups_in_measure
        result = self.convert_cups_grams(item, amount, around_words)

        return result

    def convert_oz_grams(self, item, amount, around_words):
        grams = self.oz_grams(amount)
        result = self.concatenate_result(grams, 'grams', item, *around_words)

        return result

    def convert_lb_grams(self, item, amount, around_words):
        grams = self.lb_grams(amount)
        result = self.concatenate_result(grams, 'grams', item, *around_words)

        return result

    # Simple one-line additional functions

    def fahrenheit_celsius(self, temperature):
        return round((temperature - 32)*5/9)

    def celsius_fahrenheit(self, temperature):
        return round(temperature*9/5) + 32

    def oz_grams(self, weight):
        return round(weight*28.35)

    def grams_oz(self, weight):
        return round(weight/28.35)

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
        '''

        string_numbers = amount.split()
        result = 0
        for string_number in string_numbers:
            if '/' in string_number:
                fraction_numbers = string_number.split('/')
                try:
                    result += round(int(fraction_numbers[0])/int(fraction_numbers[1]), 2)
                    return result
                except:
                    print('Error in fraction', string_number)
                    pass
            else:
                result += int(string_number)
        return result

    def concatenate_result(self, *args):
        result = ''
        for arg in args:
            if arg not in ['', 0]:
                result += str(arg) + ' '
        return result.strip()