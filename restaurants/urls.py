# restaurants/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='restaurants-home'),
    path('add/', views.add_restaurant, name='add_restaurant'),
    path('list/', views.restaurant_list, name='restaurant_list'),
    path('delete/<int:id>/', views.delete_restaurant, name='delete_restaurant'),
]
