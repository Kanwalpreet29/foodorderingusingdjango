from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

class DishCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Dish(models.Model):
    name = models.CharField(max_length=100)
    details = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='dishes/', blank=True, null=True)
    ingredients = models.TextField(blank=True, null=True)
    category = models.ForeignKey(DishCategory, on_delete=models.SET_NULL, null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class TableBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    mobile = models.CharField(max_length=15)
    date = models.DateField()
    time = models.TimeField()
    guest_count = models.IntegerField()
    special_requests = models.TextField(blank=True, null=True)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.name} at {self.restaurant.name} on {self.date} {self.time}"
