from django.urls import path
from . import views, models

urlpatterns = [
    path('', views.HomeView.as_view()),

    path('admin/', views.AdminFlightListView.as_view()),
    path('admin/login/', views.AdminLoginView.as_view()),
    path('admin/new-flight/', views.AdminCreateNewFlight.as_view()),
    path('customer/flights/', views.FlightListView.as_view()),
]
