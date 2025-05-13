import os
import sys
import sys
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Setup Django environment for ORM access
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodordering.settings")

import django
django.setup()

from products.models_order import Order
from products.models import Dish  # Import Django models
from products.models import TableBooking
from restaurants.models import Restaurant
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.conf import settings


app = Flask(__name__)

CORS(app)

def token_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Token '):
                token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token_obj = Token.objects.get(key=token)
            request.user = token_obj.user
        except Token.DoesNotExist:
            return jsonify({'message': 'Invalid token!'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api-token-auth', methods=['POST'])
def get_token():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return jsonify({'token': token.key})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401



@app.route('/order/<int:order_id>', methods=['DELETE'])
@token_required
def delete_order(order_id):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.debug(f"Received request to delete order with id: {order_id}")
    try:
        order = Order.objects.get(id=order_id)
        order.delete()
        logger.debug(f"Order {order_id} deleted successfully.")
        return jsonify({"message": f"Order {order_id} deleted successfully."})
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found.")
        return jsonify({"error": "Order not found."}), 404



@app.route('/book-table', methods=['GET'])
@token_required
def get_table_bookings():
    user = request.user
    bookings = TableBooking.objects.filter(user=user).order_by('-booked_at')
    booking_list = []
    for booking in bookings:
        booking_list.append({
            'id': booking.id,
            'name': booking.name,
            'email': booking.email,
            'mobile': booking.mobile,
            'date': booking.date.strftime('%Y-%m-%d'),
            'time': booking.time.strftime('%H:%M:%S'),
            'guest_count': booking.guest_count,
            'special_requests': booking.special_requests,
            'booked_at': booking.booked_at.strftime('%Y-%m-%d %H:%M:%S'),
            'restaurant': {
                'id': booking.restaurant.id,
                'name': booking.restaurant.name,
            }
        })
    return jsonify({'bookings': booking_list})


@app.route('/book-table', methods=['POST'])
@token_required
def create_table_booking():
    data = request.get_json()
    user = request.user

    restaurant_id = data.get('restaurant_id')
    name = data.get('name')
    email = data.get('email')
    mobile = data.get('mobile')
    date_str = data.get('date')
    time_str = data.get('time')
    guest_count = data.get('guest_count')
    special_requests = data.get('special_requests', '')

    if not all([restaurant_id, name, email, mobile, date_str, time_str, guest_count]):
        return jsonify({'message': 'Missing required booking fields'}), 400

    try:
        restaurant = Restaurant.objects.get(id=restaurant_id, is_active=True)
    except Restaurant.DoesNotExist:
        return jsonify({'message': 'Invalid restaurant ID'}), 400

    from datetime import datetime
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        time = datetime.strptime(time_str, '%H:%M:%S').time()
    except ValueError:
        return jsonify({'message': 'Invalid date or time format'}), 400

    try:
        guest_count = int(guest_count)
    except ValueError:
        return jsonify({'message': 'Guest count must be an integer'}), 400

    booking = TableBooking(
        user=user,
        restaurant=restaurant,
        name=name,
        email=email,
        mobile=mobile,
        date=date,
        time=time,
        guest_count=guest_count,
        special_requests=special_requests
    )
    booking.save()

   
    subject = "Table Booking Confirmation"
    message = (f"Dear {name},\n\nYour table has been booked successfully at "
               f"{restaurant.name} for {date_str} at {time_str}.\n\nThank you for choosing us!")
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    try:
        send_mail(subject, message, email_from, recipient_list)
    except Exception as e:
        
        import logging
        logging.error(f"Failed to send booking confirmation email: {str(e)}")

    return jsonify({'message': 'Booking created successfully', 'booking_id': booking.id}), 201


if __name__ == '__main__':
    app.run(debug=True, port=5000)
