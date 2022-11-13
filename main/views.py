import datetime
from django.views.generic import TemplateView, ListView
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.conf import settings

from main import models, forms


DEFAULT_PAGINATION_COUNT = 10


class HomeView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


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
    queryset = models.Flight.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs



class FlightListView(ListView):
    template_name = 'main/customer/flight/list.html'
    paginate_by = DEFAULT_PAGINATION_COUNT
    queryset = models.Flight.objects.annotate(
        route_number=F('schedule__route__route_number'),
        from_city=F('schedule__route__from_city__name'),
        to_city=F('schedule__route__to_city__name'),
        departure_time=F('schedule__departure_time'),
        arrival_time=F('schedule__arrival_time'),
        travel_time=F('schedule__arrival_time') - F('schedule__departure_time'),
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
        form.is_valid()
        context['form'] = form
        return context
