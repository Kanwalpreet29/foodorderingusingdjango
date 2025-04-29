from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the Restaurants homepage!")

def home(request):
    return render(request, 'restaurants/home.html')