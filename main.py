from googletrans import Translator
from converter import ARConverter


translator = Translator(service_urls=[
      'translate.google.com',
      'translate.google.co.kr',
    ])

converter = ARConverter()

my_recipe_file = open('Data/cake.txt', encoding='UTF-8')
for line in my_recipe_file.readlines():
    converter.break_line(line)
# my_recipe_words = my_recipe.split()
# translation = translator.translate(my_recipe, dest='ru')
# print(my_recipe_words)

my_recipe_file.close()


