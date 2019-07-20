'''
This module converts american measurements to russian.
Starting from temperature - Fahrenheit to Celsius
and finishing with cups/tsp/Tbsp to grams
'''

import re


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
            for line in coefficients:
                new_coefficient = line.strip().split(':')
                self.coefficients[new_coefficient[0]] = int(new_coefficient[1])

        self.ml_measures = {'tsp': 5, 'tbsp': 15, 'gallon': 3875.4, 'pint': 473, 'oz': 29.6, 'quart ': 946.4, 'cup': 240}

        self.units = [['cup', 'cups', 'c'], ['oz', 'ounce', 'ounces'], ['lb', 'pound', 'pounds'], ['gr', 'gram', 'grams']]

    def break_line(self, line):
        amount = re.findall(r'\d[\d /]+', line)
        if amount[0]:
            amount = self.convert_amount(amount[0])
        words = re.findall(r'[A-Za-z]+', line)
        for word in words:
            for i in range(len(self.units)):
                if word in self.units[i]:
                    measure = self.units[i][0]
                    words.remove(word)

            if word in self.coefficients:
                item = word
                words.remove(word)
        try:
            print(amount, end=' ')
        except: pass

        try:
            print(measure, end=' ')
        except: pass

        try:
            print(item, end=' ')
        except: pass

        print(' '.join(words))

    def convert_amount(self, amount):
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

    def cups_grams(self, item, cups):
        """Try to convert item from cups to grams if it is in self.coefficients
        dictionary. If everything went correct return new measure and TRUE flag.
        If item is not in dictionary - return input amount of cups and FALSE flag
        """

        if item in self.coefficients:
            return [round(self.coefficients[item] * cups), True]
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


