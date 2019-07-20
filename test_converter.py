import unittest

from converter import ARConverter


class TestTemperatureConvert(unittest.TestCase):

    def setUp(self) -> None:
        self.my_converter = ARConverter()

    def test_convert_amount_complete(self):
        fraction1 = self.my_converter.convert_amount('1 2/3')
        fraction2 = self.my_converter.convert_amount('3/4')

        self.assertEqual(fraction1, 1.67)
        self.assertEqual(fraction2, 0.75)


    def test_convert_amount_incomplete(self):
        fraction1 = self.my_converter.convert_amount('1 /8')
        fraction2 = self.my_converter.convert_amount('7 1/')
        fraction3 = self.my_converter.convert_amount('/9')
        fraction4 = self.my_converter.convert_amount('5/')
        fraction5 = self.my_converter.convert_amount('1 1/4 8')

        self.assertEqual(fraction1, 1)
        self.assertEqual(fraction2, 7)
        self.assertEqual(fraction3, 0)
        self.assertEqual(fraction4, 0)
        self.assertEqual(fraction5, 1.25)

    def test_cups_grams(self):
        '''Assume that we have the 'coefficients.json' file with 'butter: 227' string in it
        self.my_converter takes this data from the file and use it.
        no_item should return the same amount of cups we gave him and 'False' flag
        '''

        butter_grams = self.my_converter.cups_grams('butter', 2)
        no_item = self.my_converter.cups_grams('no_such_an_item', 4)
        self.assertEqual(butter_grams, [454, True])
        self.assertEqual(no_item, [4, False])

    def test_fahrenheit_celsius_high(self):
        celsius = self.my_converter.fahrenheit_celsius(380)
        self.assertEqual(celsius, 193)

    def test_fahrenheit_celsius_zero(self):
        celsius = self.my_converter.fahrenheit_celsius(32)
        self.assertEqual(celsius, 0)

    def test_fahrenheit_celsius_low(self):
        celsius = self.my_converter.fahrenheit_celsius(-320)
        self.assertEqual(celsius, -196)

    def test_celsius_fahrenheit_high(self):
        fahrenheit = self.my_converter.celsius_fahrenheit(220)
        self.assertEqual(fahrenheit, 428)

    def test_celsius_fahrenheit_zero(self):
        fahrenheit = self.my_converter.celsius_fahrenheit(0)
        self.assertEqual(fahrenheit, 32)

    def test_celsius_fahrenheit_low(self):
        fahrenheit = self.my_converter.celsius_fahrenheit(-100)
        self.assertEqual(fahrenheit, -148)


unittest.main()
