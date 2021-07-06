from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'home'
urlpatterns = [
    path('home/', views.home, name='home'),
    path('filtrar/', views.filtrar, name='filtrar'),
]