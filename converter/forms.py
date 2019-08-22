from django import forms

class MainForm(forms.Form):
    class Meta:
        fields = ['recipe']
        # widgets = {'text': forms.Textarea(attrs={'id': 'textarea-source'})}

    recipe = forms.CharField(label='', widget=forms.Textarea())

