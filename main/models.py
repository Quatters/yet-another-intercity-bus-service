from django.db import models
from django.db.models import Value
from django.db.models.functions import Concat


class City(models.Model):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        verbose_name_plural = 'cities'

    def __str__(self) -> str:
        return self.name

    @classmethod
    def choices(cls):
        return list(cls.objects.values_list('id', 'name'))


class BusModel(models.Model):
    name = models.CharField(max_length=128, unique=True)
    seats_amount = models.IntegerField()

    def __str__(self) -> str:
        return self.name


class Bus(models.Model):
    bus_number = models.CharField(max_length=128, unique=True)
    model = models.ForeignKey(BusModel, on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = 'buses'

    def __str__(self) -> str:
        return f'{self.bus_number} ({self.model})'

    @classmethod
    def choices(cls):
        return list(cls.objects.annotate(
            bus=Concat('bus_number', Value(' ('), 'model__name', Value(')'))
        ).values_list('id', 'bus'))


class Route(models.Model):
    route_number = models.CharField(max_length=5, unique=True)
    distance_km = models.IntegerField()
    from_city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='from_cities')
    to_city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='to_cities')

    def __str__(self) -> str:
        return f'{self.route_number} ({self.from_city} - {self.to_city})'

    @classmethod
    def choices(cls):
        return list(cls.objects.annotate(
            route=Concat(
                'route_number',
                Value(' ('),
                'from_city__name',
                Value(' - '),
                'to_city__name',
                Value(')')
            )
        ).values_list('id', 'route'))


class Schedule(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()

    def __str__(self) -> str:
        return f'{self.departure_time} - {self.arrival_time}'


class Flight(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.PROTECT)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    departure_date = models.DateField()
    arrival_date = models.DateField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ['-departure_date', 'price']

    def __str__(self) -> str:
        return f'Flight of {self.schedule}'


class Ticket(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    seat_number = models.IntegerField()
    customer_name = models.CharField(max_length=128, null=True, default=None)

    @property
    def is_bought(self):
        return self.customer_name is not None

    def __str__(self) -> str:
        return f'Ticket of {self.flight}'
