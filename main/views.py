import datetime
from django.views.generic import ListView
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Case, When, Value, DateTimeField, Model, Sum
from django.db.models.functions import Concat
from django.conf import settings

from main import models, forms


DEFAULT_PAGINATION_COUNT = 10


class HomeView(View):
    def get(self, request):
        return redirect('/customer/flights/')


class AdminLoginView(View):
    template_name = 'main/admin/login.html'

    def get(self, request):
        return render(request, self.template_name, {'form': forms.LoginForm()})

    def post(self, request):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                login(request, user)
                return redirect(self.request.GET.get('next', '/admin/'))
            else:
                form.add_error(field=None, error='Неверное имя пользователя или пароль.')

        return render(request, self.template_name, {'form': form})


class AdminFlightListView(LoginRequiredMixin, ListView):
    login_url = '/admin/login/'
    paginate_by = DEFAULT_PAGINATION_COUNT
    template_name = 'main/admin/flight/list.html'
    queryset = models.Flight.objects.order_by('-id')

    def get_queryset(self):
        qs = super().get_queryset()
        return qs


class AdminCreateNewFlight(LoginRequiredMixin, View):
    login_url = '/admin/login/'
    template_name = 'main/admin/flight/create-new.html'

    def get(self, request, *args, **kwargs):
        if from_existing := request.GET.get('from_existing'):
            try:
                flight = models.Flight.objects.get(id=from_existing)
                departure = datetime.datetime.combine(
                    flight.departure_date,
                    flight.schedule.departure_time,
                )
                arrival = datetime.datetime.combine(
                    flight.arrival_date,
                    flight.schedule.arrival_time,
                )
                form = forms.CreateNewFlightForm({
                    'route_number': flight.schedule.route.id,
                    'departure': str(departure),
                    'arrival': str(arrival),
                    'bus': flight.bus.id,
                    'price': flight.price,
                })
            except Model.DoesNotExist:
                form = forms.CreateNewFlightForm()
        else:
            form = forms.CreateNewFlightForm()

        return render(request, self.template_name, {
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = forms.CreateNewFlightForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {
                'form': form,
            })

        data = form.cleaned_data

        departure_date = form.cleaned_data['departure'].date()
        arrival_date = form.cleaned_data['arrival'].date()
        departure_time = form.cleaned_data['departure'].time()
        arrival_time = form.cleaned_data['arrival'].time()

        schedule = models.Schedule.objects.get_or_create(
            departure_time=departure_time,
            arrival_time=arrival_time,
            route=data['route_number'],
        )[0]

        flight = models.Flight.objects.create(
            bus=data['bus'],
            schedule=schedule,
            departure_date=departure_date,
            arrival_date=arrival_date,
            price=data['price'],
        )

        ticket_count = data['bus'].model.seats_amount
        for i in range(1, ticket_count + 1):
            models.Ticket.objects.create(flight=flight, seat_number=i)

        return redirect('/admin/')


class FlightListView(ListView):
    template_name = 'main/customer/flight/list.html'
    paginate_by = DEFAULT_PAGINATION_COUNT
    queryset = models.Flight.objects.annotate(
        route_number=F('schedule__route__route_number'),
        from_city=F('schedule__route__from_city__name'),
        to_city=F('schedule__route__to_city__name'),
        departure_time=F('schedule__departure_time'),
        arrival_time=F('schedule__arrival_time'),
        travel_time=(
            Concat(
                'arrival_date',
                Value(' '),
                'schedule__arrival_time',
                output_field=DateTimeField()
            )
            - Concat(
                'departure_date',
                Value(' '),
                'schedule__departure_time',
                output_field=DateTimeField()
            )
        ),
    )

    def get_queryset(self):
        qs = self.queryset
        if from_city := self.request.GET.get('from_city'):
            qs = qs.filter(schedule__route__from_city=from_city)
        if to_city := self.request.GET.get('to_city'):
            qs = qs.filter(schedule__route__to_city=to_city)
        if date := self.request.GET.get('departure_date'):
            qs = qs.filter(departure_date=date)
        if not settings.CUSTOMER_SHOW_OLD_FLIGHTS:
            qs = qs.filter(departure_date__gte=datetime.date.today())
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.SearchFlightForm(self.request.GET)
        if not form.data:
            form = forms.SearchFlightForm()
        form.is_valid()
        context['form'] = form
        return context


class FlightDetailView(ListView):
    template_name = 'main/customer/flight/detail.html'

    def get_queryset(self):
        return models.Ticket.objects.filter(
            flight=self.kwargs['flight_id']
        ).annotate(disabled=Case(
            When(customer_name__isnull=True, then=Value(False)),
            default=Value(True),
        ))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = forms.BuyTicketForm(flight_id=self.kwargs['flight_id'])

        context['form'] = form

        qs = self.get_queryset()
        count = qs.count()
        extra = 0
        if (extra := count % 4) != 0:
            count -= extra
        context['divide_on'] = [
            count // 4,
            count // 2,
            count - count // 4,
        ]
        ticket_list = list(qs)
        context['common_tickets'] = ticket_list[:count]
        context['extra_tickets'] = ticket_list[count:]
        context['extra'] = extra
        context['half'] = count // 2
        context['count'] = count
        return context

    def post(self, request, **kwargs):
        flight_id = kwargs['flight_id']
        form = forms.BuyTicketForm(self.request.POST, flight_id=flight_id)
        self.object_list = self.get_queryset()
        context = self.get_context_data(**kwargs)
        if form.is_valid():
            data = form.cleaned_data
            ticket_qs = models.Ticket.objects.filter(id__in=data['ticket'])

            ticket_qs.update(customer_name=data['name'])
            context['buy_data'] = {
                'flight': ticket_qs.first().flight,
                'sum': ticket_qs.aggregate(sum=Sum('flight__price'))['sum'],
                'count': ticket_qs.count(),
                'tickets': list(ticket_qs),
                'customer': data['name'],
            }
        context.update(self.get_context_data(**kwargs))
        return self.render_to_response(context)
