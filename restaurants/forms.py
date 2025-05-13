from django import forms
from .models import Restaurant

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'description', 'address', 'phone', 'email', 'website', 'opening_time', 'closing_time', 'image', 'location', 'rating']
