from django import forms

class MainForm(forms.Form):
    class Meta:
        fields = ['recipe']

    recipe = forms.CharField(label='', widget=forms.Textarea())
