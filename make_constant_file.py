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

class MeasurementsFileMaker():

    def __init__(self):
        self.coefficients = []
        self.uniq_coefficients = []
        self.multi_coefficients = []

        self.make_measurements_file()

    def make_measurements_file(self):
        """Make coefficients and write it in the coefficients.json file"""

        self.make_coefficients()

        with open('coefficients.json', 'w+') as coefficient:
            for measure in sorted(self.coefficients):
                if len(measure) == 2:
                    coefficient.write(measure[0] + ':' + measure[1] + '\n')
                else:
                    coefficient.write('{}, {}: {}\n'.format(measure[0],
                                                          ' '.join(measure[i] for i in range(1, len(measure)-1)), measure[-1]))

    def make_coefficients(self):
        """Read measurements.txt file with raw messy input of coefficients,
        and handle every line separately. Start processing items with more than one word in the name -
        Bread flour for example.
        """

        measurements_file = open('measurements.txt', 'r')
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
            self.coefficients.append([x.lower() for x in items] + weight)
            self.uniq_coefficients.append(items[0].lower())
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
        for example, for 'Brown Sugar' we have to have single 'Sugar' item"""

        check = False
        for i in range(len(multi_item) - 1):
            if multi_item[i] in self.uniq_coefficients:
                multi_item[0], multi_item[i] = multi_item[i], multi_item[0]
                check = True
                break
        if not check:
            print('No initial item for multi-item', multi_item)
        self.coefficients.append(multi_item)

