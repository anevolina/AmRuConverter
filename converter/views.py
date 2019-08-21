from django.shortcuts import render
from . import forms
from .my_converter.converter import ARConverter
from googletrans import Translator


# Create your views here.

def index(request):
    conv_recipe = 'Перевод'
    English = True

    if request.method != 'POST':
        form = forms.MainForm()


    else:
        form = forms.MainForm(request.POST)

        if form.is_valid():

            converter = ARConverter()
            text = form.cleaned_data['recipe']
            conv_recipe = ''
            for line in text.split('\n'):
                conv_recipe += converter.process_line(line) + '\n'

            to_translate = request.POST.get('to_translate')
            if to_translate == 'RU':
                English = False
                translator = Translator(service_urls=[
                'translate.google.com',
                'translate.google.co.kr',                ])
                translation = translator.translate(conv_recipe, dest='ru')
                conv_recipe = translation.text


    context = {'form': form, 'translation': conv_recipe, 'En': English}

    return render(request, 'converter/index.html', context)
