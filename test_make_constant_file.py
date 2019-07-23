"""Became irrelevant"""

# import unittest
#
# from make_constant_file import return_measurements_dic
#
#
# class TestAdditionalFunctions(unittest.TestCase):
#
#     def test_return_measurements_dic_simple(self):
#         new_line = return_measurements_dic('all-purpose flour, 128')
#         self.assertEqual(new_line, 'all purpose flour:128')
#
#     def test_return_measurements_dic_other_caracters(self):
#         new_line = return_measurements_dic('bread flour%^:;_.:136@"')
#         self.assertEqual(new_line, 'bread flour:136')
#
#     def test_return_measurements_dic_spaces(self):
#         new_line = return_measurements_dic('  bread $ flour   % ^ : ;_ -: 136 @ "   ')
#         self.assertEqual(new_line, 'bread flour:136')
#
#
# unittest.main()
