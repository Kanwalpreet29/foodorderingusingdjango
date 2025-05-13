from django.db import models

# Create your models here.


class Restaurant(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='restaurant_images/', default='restaurant_images/default_image.jpg')  # Update this line
    location = models.CharField(max_length=255)
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)

    def __str__(self):
        return self.name
