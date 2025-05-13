from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the Restaurants homepage!")

from django.shortcuts import redirect

def home(request):
    return redirect('restaurant_list')

from django.shortcuts import render, redirect
from .forms import RestaurantForm

def add_restaurant(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('restaurant_list')
    else:
        form = RestaurantForm()
    return render(request, 'restaurants/add_restaurant.html', {'form': form})


#from django.shortcuts import render
from .models import Restaurant

def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'restaurants/home.html', {'restaurants': restaurants})

def delete_restaurant(request, id):
    restaurant = Restaurant.objects.get(id=id)
    restaurant.delete()
    return redirect('restaurant_list')
