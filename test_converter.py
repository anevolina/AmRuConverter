import unittest

from converter import ARConverter


class TestTemperatureConvert(unittest.TestCase):

    def setUp(self) -> None:
        self.my_converter = ARConverter()

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
