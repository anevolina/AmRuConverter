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

        self.ml_measures = {'tbsp': 15, 'gallon': 3875.4, 'pint': 473, 'oz': 29.6, 'quart ': 946.4, 'cup': 240}

        self.units = [['cup', 'cups', 'c'], ['oz', 'ounce', 'ounces'], ['lb', 'pound', 'pounds'],
                      ['gr', 'gram', 'grams'], ['tsp', 'teaspoon'], ['tbsp', 'tablespoon'], ['gallon', 'gallons'],
                      ['pint', 'pints'], ['quart', 'quarts']]

    def break_line(self, line):
        """Divide line into amount, measure, item and another words in it"""

        result = {'amount': 0, 'measure': '', 'item': '', 'words': ''}
        amount = re.findall(r'\d[\d /]+', line)
        if amount[0]:
            amount = self.str_to_int_convert_amount(amount[0])
            result.update({'amount': amount})
        words = re.findall(r'[A-Za-z]+', line)
        for word in words:
            for i in range(len(self.units)):
                if word.lower() in self.units[i]:
                    measure = self.units[i][0]
                    words.remove(word)
                    result.update({'measure': measure})

            if word in self.coefficients:
                words.remove(word)
                result.update({'item': word})

        result.update({'words': words})
        # print(result)
        return result

    def process_line(self, line):
        components = self.break_line(line)
        item = components['item']
        measure = components['measure']
        amount = components['amount']
        around_words = components['words']

        if measure == 'cup':
            cups_to_grams = self.cups_grams(item, amount, around_words)
            if cups_to_grams[1]:
                # result = ' '.join([str(cups_to_grams[0]), 'grams', item] + around_words)
                result = self.concatenate_result(cups_to_grams[0], 'grams', item, *around_words)

            # else:
                # result = ' '.join([str(amount), measure, item] + around_words)

        elif measure == 'oz':
            grams = self.oz_grams(amount)
            result = self.concatenate_result(grams, 'grams', item, *around_words)

        else:
            # result = ' '.join([str(amount), measure, item] + around_words)
            result = self.concatenate_result(amount, measure, item, *around_words)

        return result + '\n'

    def concatenate_result(self, *args):
        result = ''
        for arg in args:
            if arg != '':
                result += str(arg) + ' '
        return result.strip()

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

    def cups_grams(self, item, cups, words):
        """Try to convert item from cups to grams if it is in self.coefficients
        dictionary. If everything went correct return new measure and TRUE flag.
        If item is not in dictionary - return input amount of cups and FALSE flag
        """
        item_in_coefficients = self.coefficients.get(item)
        if item_in_coefficients:
            if type(self.coefficients[item]) == dict:

                for spec in words:
                    spec_in_dic = self.coefficients[item].get(spec)
                    if spec_in_dic:
                        grams = self.coefficients[item][spec] * cups
                        break
                    grams = self.coefficients[item][''] * cups

            else:
                grams = self.coefficients[item] * cups

            return [grams, True]
        else:
            print('INVALID PRODUCT: ', item)
            return [cups, False]

    def fahrenheit_celsius(self, temperature):
        return round((temperature - 32)*5/9)

    def celsius_fahrenheit(self, temperature):
        return round(temperature*9/5) + 32

    def oz_grams(self, weight):
        return round(weight*28.35)

    def grams_oz(self, weight):
        return round(weight/28.35)

    def ml_cups(self, ml):
        return round(ml/240)


