from django.db import models
from django.contrib.auth.models import User
from products.models import Profile

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING_DELIVERY', 'Pending Delivery'),
        ('PAID', 'Paid'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    customer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)  # Store dish name as string instead of ForeignKey
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING_DELIVERY')
    invoice_id = models.CharField(max_length=100, blank=True, null=True)
    ordered_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.invoice_id} by {self.customer.user.username}"

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Status {self.status} for Order {self.order.invoice_id} at {self.updated_at}"
