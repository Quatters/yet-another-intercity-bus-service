from datetime import timedelta
from secrets import choice
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from main import models


class LoginForm(forms.Form):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')


class CreateNewFlightForm(forms.Form):
    route_number = forms.ModelChoiceField(
        queryset=models.Route.objects,
        label='Маршрут',
    )
    departure = forms.DateTimeField(
        label='Отправление',
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'}
        )
    )
    arrival = forms.DateTimeField(
        label='Прибытие',
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'}
        )
    )
    bus = forms.ModelChoiceField(
        queryset=models.Bus.objects,
        label='Автобус',
    )
    price = forms.DecimalField(label='Цена билета')

    def clean(self):
        departure = self.cleaned_data.get('departure')
        arrival = self.cleaned_data.get('arrival')
        if departure and arrival and departure >= arrival:
            raise ValidationError(
                'Дата прибытия должна быть позже, чем дата отправления.',
            )
        return self.cleaned_data

    def clean_departure(self):
        departure = self.cleaned_data.get('departure')
        if departure <= timezone.now() + timedelta(days=3):
            raise ValidationError(
                'Дата отправления должна быть не ранее, чем за три дня, начиная от текущего дня.'
            )
        return departure


class SearchFlightForm(forms.Form):
    from_city = forms.ModelChoiceField(
        queryset=models.City.objects,
        empty_label='Откуда...',
        label='Откуда',
        initial=models.City.objects.get(name='Владивосток')
    )
    to_city = forms.ModelChoiceField(
        queryset=models.City.objects,
        empty_label='Куда...',
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


class BuyTicketForm(forms.Form):
    def __init__(self, *args, **kwargs):
        flight_id = kwargs.pop('flight_id')
        self.base_fields['ticket'].choices = models.Ticket.seat_choices(flight_id)
        super().__init__(*args, **kwargs)

    ticket = forms.TypedMultipleChoiceField(
        coerce=int,
        label='Место',
    )
    name = forms.CharField(label="Покупатель")
