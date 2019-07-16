'''
This module converts american measurements to russian.
Starting from temperature - Fahrenheit to Celsius
and finishing with cups/tsp/Tbsp to grams
'''


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

        self.ml_measures = {'tsp': 5, 'tbsp': 15, 'gallon': 3875.4, 'pint': 473, 'oz': 29.6, 'quart ': 946.4}

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


