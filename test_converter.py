import unittest

from converter import ARConverter


class TestTemperatureConvert(unittest.TestCase):

    def setUp(self) -> None:
        self.my_converter = ARConverter()
        self.number_dict = {'amount': {}, 'measure': {}, 'old_measure': {}, 'F_word': {}, 'possible_F': {}}

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

    def test_process_line_cup(self):
        line1 = self.my_converter.process_line('1 c milk')
        line2 = self.my_converter.process_line('1 1/2 cup milk')
        line3 = self.my_converter.process_line('0 cups milk')
        self.assertEqual(line1, '244 grams milk')
        self.assertEqual(line2, '366 grams milk')
        self.assertEqual(line3, '0 grams milk')

    def test_process_line_oz(self):
        line1 = self.my_converter.process_line('1 oz milk')
        line2 = self.my_converter.process_line('1 1/2 ounces milk')
        line3 = self.my_converter.process_line('0 ounce milk')
        self.assertEqual(line1, '28 grams milk')
        self.assertEqual(line2, '43 grams milk')
        self.assertEqual(line3, '0 grams milk')

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
        self.assertEqual(line3, '0 grams milk')

    def test_delete_incorrect_symbols(self):
        line1 = self.my_converter.delete_incorrect_symbols('¼ cups all purpose flour')
        line2 = self.my_converter.delete_incorrect_symbols('1 ½ cups all purpose flour')
        line3 = self.my_converter.delete_incorrect_symbols('Preheat the oven to 350°F')
        self.assertEqual(line1, '1/4 cups all purpose flour')
        self.assertEqual(line2, '1 1/2 cups all purpose flour')
        self.assertEqual(line3, 'Preheat the oven to 350F')

    def test_find_numbers(self):
        number1 = self.my_converter.find_numbers('1 16 oz can of lentils')
        number2 = self.my_converter.find_numbers('1 1/2 cup of milk')
        number3 = self.my_converter.find_numbers('3.5 oz sugar')
        number4 = self.my_converter.find_numbers('1,8 lb butter')
        numbers56 = self.my_converter.find_numbers('1 pack 8 oz cheese')

        self.assertEqual(number1, ['1 16'])
        self.assertEqual(number2, ['1 1/2'])
        self.assertEqual(number3, ['3.5'])
        self.assertEqual(number4, ['1,8'])
        self.assertEqual(numbers56, ['1', '8'])

    def test_look_around_number(self):
        words1 = self.my_converter.look_around_number('16 oz can', '16', self.number_dict)
        words2 = self.my_converter.look_around_number('butter 1 lb', '1', self.number_dict)
        words3 = self.my_converter.look_around_number('sugar lb 10', '10', self.number_dict)

        self.assertEqual(words1, [' oz'])
        self.assertEqual(words2, ['butter ', ' lb'])
        self.assertEqual(words3, ['lb ', ''])

    def test_update_farenheits(self):
        line1 = self.my_converter.update_farenheits('Preheat oven till 350 F', {'amount': 350, 'F_word': 'F'})
        line2 = self.my_converter.update_farenheits('Preheat oven till 250', {'amount': 250})

        self.assertEqual(line1, 'Preheat oven till 177 C')
        self.assertEqual(line2, 'Preheat oven till 121')




unittest.main()
