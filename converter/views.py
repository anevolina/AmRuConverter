from django.shortcuts import render
from . import forms
from .my_converter.converter import ARConverter
from googletrans import Translator


# Create your views here.

def index(request):
    translation = 'Перевод'
    if request.method != 'POST':
        form = forms.MainForm()

    else:
        form = forms.MainForm(request.POST)
        if form.is_valid():
            converter = ARConverter()
            translator = Translator(service_urls=[
                'translate.google.com',
                'translate.google.co.kr',
            ])
            text = form.cleaned_data['recipe']
            recipe = ''
            for line in text.split('\n'):
                recipe += converter.process_line(line) + '\n'
            translation = translator.translate(recipe, dest='ru')
            translation = translation.text

    context = {'form': form, 'translation': translation}

    return render(request, 'converter/index.html', context)
