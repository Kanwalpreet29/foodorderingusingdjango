from django.contrib import admin
from django.http import JsonResponse
from django.template.response import TemplateResponse
import requests  # for calling external APIs like Flask

from products.models import Dish, DishCategory, Profile

admin.site.site_header = "YumYield | Admin"

class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'subject', 'added_on', 'is_approved']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

class TeamAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'added_on', 'updated_on']

class DishAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price']

admin.site.register(Dish, DishAdmin)
admin.site.register(DishCategory, CategoryAdmin)
admin.site.register(Profile)

# Define custom admin for Order model
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'item', 'status', 'invoice_id', 'ordered_on')
    search_fields = ['customer__user__first_name', 'item__name']
    list_filter = ['status', 'ordered_on']

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Removed fetching data from Flask API for sales report
        return super().changelist_view(request, extra_context=extra_context)

# Register the Order model with custom admin interface
# Removed registration of Order as it is not defined in products.models
    def get_sales_report(self, request):
        try:
            # Fetch data from Flask API (make sure the Flask server is running)
            response = requests.get('http://localhost:5000/daily_sales_report')  # Flask API call
            if response.status_code == 200:
                data = response.json()
                return data['daily_sales']  # Adjust based on the response format
            else:
                return "Failed to fetch sales data"
        except Exception as e:
            return f"Error: {str(e)}"


