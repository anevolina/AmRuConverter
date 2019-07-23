"""
There is a one-time running file, which takes all data from the file
measurements.txt, read it line-by-line and compile JSON file with dictionary
key = item, value = grams in 1 cup, separated by ':' symbol
for multi-word items it should be the main initial item - for example, for 'Brown Sugar'
we have to have single 'Sugar' and it will look like
sugar:200
sugar, brown:220
"""

import re
import json
from os.path import join, dirname

class MeasurementsFileMaker():

    def __init__(self, path):
        self.multi_coefficients = []
        self.dic_coefficients = {}

        self.path = join(dirname(__file__), path)

        self.make_measurements_file()

    def make_measurements_file(self):
        """Make coefficients and write it in the coefficients.json file"""

        self.make_coefficients()

        with open('coefficients.json', 'w+') as coefficient:
            json.dump(self.dic_coefficients, coefficient)

    def make_coefficients(self):
        """Read measurements.txt file with raw messy input of coefficients,
        and handle every line separately. Start processing items with more than one word in the name -
        Bread flour for example.
        """

        measurements_file = open(self.path, 'r')
        for line in measurements_file:
            if line == '\n' or line.strip()[0] == '#':
                continue
            self.process_line(line)
        measurements_file.close()

        self.process_multi_coefficients()

    def process_line(self, line):
        """Divide a line for words and numbers. If there are more than one word, handle this item separately"""

        items = re.findall(r'[A-Za-z-]+', line)
        weight = re.findall(r'[\d]+', line)

        if len(items) == 1:
            self.dic_coefficients[items[0].lower()] = int(weight[0])
        else:
            self.multi_coefficients.append([x.lower() for x in items] + weight)

    def process_multi_coefficients(self):
        """If there are items with more than one word in the name, process these items"""

        if len(self.multi_coefficients) > 0:
            for multi_item in self.multi_coefficients:
                self.parse_multi_item(multi_item)
        pass

    def parse_multi_item(self, multi_item):
        """ We have to check that there is an initial item for every multi-word item -
        for example, for 'Brown Sugar' we have to have single 'Sugar' item.
        If there is no initial item - it could be missed"""

        check = False
        for i in range(len(multi_item) - 1):
            item_in_dictionary = self.dic_coefficients.get(multi_item[i])
            if item_in_dictionary:
                self.add_multi_item_in_dic(multi_item, i)

                check = True
                break
        if not check:
            print('No initial item for multi-item', multi_item)
            item_name = ' '.join(multi_item[i] for i in range(len(multi_item)-1))
            self.dic_coefficients.update({item_name: int(multi_item[-1])})



    def add_multi_item_in_dic(self, item, position):
        """Add sub dictionary for items with multiple measures - such as sugar -
        we have different weight in 1cup of brown, powdered, granulated, etc"""

        item_name = item[position]
        previous_coef = self.dic_coefficients[item_name]
        item.remove(item_name)
        item_spec = ' '. join(item[i] for i in range(len(item) - 1))

        if not type(previous_coef) == dict:
            self.dic_coefficients.update({item_name: {'': previous_coef, item_spec: int(item[-1])}})
        else:
            self.dic_coefficients[item_name].update({item_spec: int(item[-1])})
        pass



start = MeasurementsFileMaker('measurements.txt')
