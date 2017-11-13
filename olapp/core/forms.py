from django import forms
from django.utils.html import strip_tags


class SearchForm(forms.Form):
    q = forms.CharField(label='Query', required=False)

    def clean_q(self):
        return strip_tags(self.cleaned_data['q'])
