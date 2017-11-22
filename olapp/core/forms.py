from datetime import date
from django import forms

from .sanitizers import extract_text, strip_all_tags


class SearchForm(forms.Form):
    q = forms.CharField(label='Query', required=False)

    def clean_q(self):
        return extract_text(self.cleaned_data['q'])


class LoginForm(forms.Form):
    openid_uid = forms.CharField(label='OpenID', required=True)


class NewReportForm(forms.Form):
    INPUT_CLASS = 'form-control form-control-sm'
    ERROR_CLASS = 'is-invalid'

    title = forms.CharField(
        label='titulek',
        widget=forms.TextInput(attrs={'class': INPUT_CLASS}),
    )
    body = forms.CharField(
        label='report',
        widget=forms.Textarea(attrs={'class': INPUT_CLASS}),
    )
    received_benefit = forms.CharField(
        label='přijaté výhody',
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS}),
    )
    provided_benefit = forms.CharField(
        label='poskytnuté výhody',
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS}),
    )
    date = forms.DateField(
        label='datum schůzky',
        initial=date.today,
        widget=forms.DateInput(attrs={'class': INPUT_CLASS + ' col-md-2'}),
    )

    def is_valid(self):
        valid = super(NewReportForm, self).is_valid()
        for f in self.errors:
            self.fields[f].widget.attrs.update({
                'class': self.fields[f].widget.attrs.get('class', '') + ' ' + self.ERROR_CLASS,
            })
        return valid

    def clean_title(self):
        return strip_all_tags(self.cleaned_data['title'])

    def clean_body(self):
        return strip_all_tags(self.cleaned_data['body'])

    def clean_received_benefit(self):
        return strip_all_tags(self.cleaned_data['received_benefit'])

    def clean_provided_benefit(self):
        return strip_all_tags(self.cleaned_data['provided_benefit'])
