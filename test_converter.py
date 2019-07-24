import unittest

from converter import ARConverter


class TestTemperatureConvert(unittest.TestCase):

    def setUp(self) -> None:
        self.my_converter = ARConverter()

    def test_str_to_int_convert_amount_complete(self):
        fraction1 = self.my_converter.str_to_int_convert_amount('18 2/3')
        fraction2 = self.my_converter.str_to_int_convert_amount('3/4')

        self.assertEqual(fraction1, 18.67)
        self.assertEqual(fraction2, 0.75)


    def test_str_to_int_convert_amount_incomplete(self):
        fraction1 = self.my_converter.str_to_int_convert_amount('1 /8')
        fraction2 = self.my_converter.str_to_int_convert_amount('7 1/')
        fraction3 = self.my_converter.str_to_int_convert_amount('/9')
        fraction4 = self.my_converter.str_to_int_convert_amount('5/')
        fraction5 = self.my_converter.str_to_int_convert_amount('1 1/4 8')

        self.assertEqual(fraction1, 1)
        self.assertEqual(fraction2, 7)
        self.assertEqual(fraction3, 0)
        self.assertEqual(fraction4, 0)
        self.assertEqual(fraction5, 1.25)


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

    def test_process_line_cup(self):
        line1 = self.my_converter.process_line('1 c milk')
        line2 = self.my_converter.process_line('1 1/2 cup milk')
        line3 = self.my_converter.process_line('0 cups milk')
        self.assertEqual(line1, '244 grams milk')
        self.assertEqual(line2, '366 grams milk')
        self.assertEqual(line3, 'grams milk')

    def test_process_line_oz(self):
        line1 = self.my_converter.process_line('1 oz milk')
        line2 = self.my_converter.process_line('1 1/2 ounces milk')
        line3 = self.my_converter.process_line('0 ounce milk')
        self.assertEqual(line1, '28 grams milk')
        self.assertEqual(line2, '43 grams milk')
        self.assertEqual(line3, 'grams milk')

    def test_process_line_tsp(self):
        line1 = self.my_converter.process_line('1 tsp soda')
        line2 = self.my_converter.process_line('1 1/2 teaspoon soda')
        self.assertEqual(line1, '1 tsp soda')
        self.assertEqual(line2, '1.5 tsp soda')

    def test_process_line_ml(self):
        line1 = self.my_converter.process_line('1 tbsp milk')
        line2 = self.my_converter.process_line('8 1/2 pints milk')
        line3 = self.my_converter.process_line('0 gallons milk')
        self.assertEqual(line1, '15 grams milk')
        self.assertEqual(line2, '4088 grams milk')
        self.assertEqual(line3, 'grams milk')



unittest.main()
