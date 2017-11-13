import re
from django import forms
from django.utils.html import strip_tags


class SearchForm(forms.Form):
    q = forms.CharField(label='Query', required=False)

    def clean_q(self):
        value = self.cleaned_data['q']
        value = strip_tags(value)
        return ' '.join(re.findall(r'(\b\w+)', value))
