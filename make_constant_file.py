"""
There is a one-time running file, which takes all data from the file
measurements.txt, read it line-by-line and compile JSON file with dictionary
key = item, value = grams in 1 cup, separated by ':' symbol
"""

import re


def return_measurements_dic(line):
    """
    Remove all excess symbols from a line, and return it as a string
    weight - it's the first numeric input in the file
    item - it's all letters. Make sure do not input 'grams/oz' or something similar in the file
    all we need there - is an item and it's weight in 1 cup
    """

    items = re.findall(r'[A-Za-z]+', line)
    weight = re.findall(r'[\d]+', line)
    # print((str(' '.join(items)) + ':' + str(weight[0])).lower())
    return (str(' '.join(items)) + ':' + str(weight[0])).lower()


def make_measurements_file():
    """
    Read measurements.txt, process and write all lines below the second
    line in coefficients.json. First two lines in measurements.txt may be used as comments
    with requirements how to write down new entry...just in case I forget it.
    """

    with open('coefficients.json', 'w+') as coefficient:
        measurements_file = open('measurements.txt', 'r')
        for line in measurements_file:
            if line == '\n' or line.strip()[0] == '#':
                continue
            new_coefficient = return_measurements_dic(line)
            coefficient.write(new_coefficient + '\n')

    measurements_file.close()

make_measurements_file()
