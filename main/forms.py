from django import forms
from django.core.exceptions import ValidationError
from main import models


class LoginForm(forms.Form):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')


class SearchFlightForm(forms.Form):
    from_city = forms.ChoiceField(
        choices=[('', 'Откуда...')] + models.City.choices(),
        label='Откуда'
    )
    to_city = forms.ChoiceField(
        choices=[('', 'Куда...')] + models.City.choices(),
        label='Куда'
    )
    departure_date = forms.DateField(
        required=False,
        label='Дата выезда',
        widget=forms.DateInput(
            format=('%d/%m/%Y'),
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        )
    )

    def clean(self):
        from_city = self.cleaned_data.get('from_city')
        to_city = self.cleaned_data.get('to_city')
        if from_city and to_city and from_city == to_city:
            raise ValidationError('Пункт отправления и пункт прибытия должны различаться.')
        return self.cleaned_data
