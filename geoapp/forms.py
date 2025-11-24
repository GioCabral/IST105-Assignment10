from django import forms

CONTINENT_CHOICES = [
    ('Africa', 'Africa'),
    ('Americas', 'Americas'),
    ('Asia', 'Asia'),
    ('Europe', 'Europe'),
    ('Oceania', 'Oceania'),
]

class ContinentForm(forms.Form):
    continent = forms.ChoiceField(
        choices=CONTINENT_CHOICES,
        label='Choose a continent'
    )
