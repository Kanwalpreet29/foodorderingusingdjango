import random
import string
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, reverse, redirect


from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if not all([name, email, subject, message]):
            messages.error(request, "Please fill in all fields.")
            return render(request, 'contact.html')

        # Compose thank you email to user
        thank_you_subject = "Thank you for contacting us"
        thank_you_message = f"Dear {name},\n\nThank you for contacting us. We have received your message and will consider your words.\n\nBest regards,\nFood Ordering Team"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]

        try:
            send_mail(thank_you_subject, thank_you_message, email_from, recipient_list)
            messages.success(request, "Thank you for contacting us. A confirmation email has been sent to you.")
        except Exception as e:
            messages.error(request, f"Failed to send confirmation email: {str(e)}")

        return render(request, 'contact.html')

    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def team_members(request):
    return render(request, 'team.html')

def services(request):
    return render(request, 'services.html')

def faq(request):
    return render(request, 'faq.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_conditions(request):
    return render(request, 'terms_conditions.html')

from products.models import Dish

def all_dishes(request):
    category_id = request.GET.get('q')
    if category_id:
        dishes = Dish.objects.filter(category__id=category_id)
    else:
        dishes = Dish.objects.all()
    context = {'dishes': dishes}
    return render(request, 'all_dishes.html', context)

from django.contrib.auth.models import User
from django.contrib.auth import login
from products.models import Profile
from django.contrib import messages

def register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('pass')
        re_pass = request.POST.get('re_pass')
        contact_number = request.POST.get('number')

        context = {
            'name': name,
            'email': email,
            'contact_number': contact_number,
        }

        if not all([name, email, password, re_pass, contact_number]):
            messages.error(request, "Please fill in all fields.")
            return render(request, 'register.html', context)

        if password != re_pass:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html', context)

        if User.objects.filter(username=email).exists():
            messages.error(request, "User with this email already exists.")
            return render(request, 'register.html', context)

        try:
            user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
            profile = Profile(user=user, contact_number=contact_number)
            profile.save()
            messages.success(request, "User registered successfully. Please log in.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error during registration: {str(e)}")
            return render(request, 'register.html', context)

    else:
        return render(request, 'register.html')

from django.http import JsonResponse
from django.contrib.auth.models import User
from products.models import Profile
from products.models_cart import Cart, CartItem
from products.models_order import Order
from products.models_cart import Cart, CartItem

def check_user_exists(request):
    username = User.objects.filter(username=request.GET.get('username')).exists()
    return JsonResponse({'exists': username})

from django.contrib.auth.decorators import login_required
from django.utils import timezone

from django.conf import settings
import logging
from restaurants.models import Restaurant

from django.http import JsonResponse

@login_required
def book_table(request):
    from django.http import JsonResponse
    if request.method == 'POST':
        restaurant_id = request.POST.get('restaurant')
        booking_date = request.POST.get('date')
        booking_time = request.POST.get('time')
        user_email = request.user.email

        # Validate restaurant selection
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id, is_active=True)
        except (Restaurant.DoesNotExist, ValueError, TypeError):
            error_message = 'Please select a valid restaurant.'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message})
            else:
                messages.error(request, error_message)
                return redirect('book_table')

        if not booking_date or not booking_time:
            error_message = 'Please provide both booking date and time.'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message})
            else:
                messages.error(request, error_message)
                return redirect('book_table')

        if not user_email:
            error_message = 'User email not found. Cannot send confirmation email.'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message})
            else:
                messages.error(request, error_message)
                return redirect('book_table')

        subject = "Table Booking Confirmation"
        message = (f"Dear {request.user.first_name},\n\nYour table has been booked successfully at "
                   f"{restaurant.name} for {booking_date} at {booking_time}.\n\nThank you for choosing us!")
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user_email]

        try:
            send_mail(subject, message, email_from, recipient_list)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                messages.success(request, "Your table has been booked. A confirmation email has been sent.")
                return redirect('book_table')
        except Exception as e:
            logging.error(f"Failed to send booking confirmation email: {str(e)}")
            error_message = 'Booking successful but failed to send email. Please contact support.'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message})
            else:
                messages.warning(request, error_message)
                return redirect('book_table')

    # Handle GET request explicitly by rendering booking.html with restaurants
    if request.method == 'GET':
        restaurants = Restaurant.objects.filter(is_active=True)
        return render(request, 'booking.html', {'restaurants': restaurants})

    # For other HTTP methods, return method not allowed response
    from django.http import HttpResponseNotAllowed
    return HttpResponseNotAllowed(['GET', 'POST'])

from products.models import DishCategory

def index(request):
    categories = DishCategory.objects.all()
    context = {'categories': categories}
    return render(request, 'index.html', context)
from products.models_cart import Cart, CartItem
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Existing imports and code unchanged...

@login_required
def add_to_cart(request, dish_id):
    user = request.user
    dish = get_object_or_404(Dish, id=dish_id)
    cart, created = Cart.objects.get_or_create(user=user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, dish=dish)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"Added {dish.name} to your cart.")
    return redirect('view_cart')

@login_required
def view_cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    items = cart.items.select_related('dish').all()
    total_price = 0
    for item in items:
        item.subtotal = item.dish.discounted_price * item.quantity
        total_price += item.subtotal
    context = {
        'cart': cart,
        'items': items,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)

from django.core.exceptions import ObjectDoesNotExist

@login_required
def remove_from_cart(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        cart_item.delete()
        messages.success(request, "Item removed from your cart.")
    except ObjectDoesNotExist:
        messages.error(request, "The item you are trying to remove does not exist in your cart.")
    return redirect('view_cart')

# Rest of the existing code unchanged...

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(email, otp_code):
    subject = 'Your OTP Code'
    message = f'Your OTP code for login is: {otp_code}. It is valid for 5 minutes.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

import logging

import requests

from django.contrib import messages

def signin(request):
    context = {}
    storage = messages.get_messages(request)
    for message in storage:
        context['message'] = message.message
        if message.level_tag == 'error':
            context['class'] = 'alert-danger'
        elif message.level_tag == 'success':
            context['class'] = 'alert-success'
        else:
            context['class'] = 'alert-info'

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        otp_input = request.POST.get('otp')

        if otp_input:
            # OTP verification step
            otp_code = request.session.get('otp_code')
            otp_user_id = request.session.get('otp_user_id')
            otp_expiry_str = request.session.get('otp_expiry')

            if not otp_code or not otp_user_id or not otp_expiry_str:
                context.update({'message': 'OTP session expired. Please login again.', 'class': 'alert-danger'})
                return render(request, 'login.html', context)

            otp_expiry = timezone.datetime.fromisoformat(otp_expiry_str)
            if timezone.now() > otp_expiry:
                context.update({'message': 'OTP expired. Please login again.', 'class': 'alert-danger'})
                return render(request, 'login.html', context)

            if otp_input == otp_code:
                from django.contrib.auth.models import User
                user = User.objects.get(id=otp_user_id)
                login(request, user)
                # Clear OTP session data
                del request.session['otp_code']
                del request.session['otp_user_id']
                del request.session['otp_expiry']
                return redirect('dashboard')
            else:
                context.update({'message': 'Invalid OTP. Please try again.', 'class': 'alert-danger'})
                context['show_otp'] = True
                context['email'] = email
                return render(request, 'login.html', context)

        else:
            # Initial login step
            if email and password:
                user = authenticate(username=email, password=password)
                if user:
                    if user.is_active:
                        # Generate OTP and send email
                        otp_code = generate_otp()
                        send_otp_email(email, otp_code)
                        request.session['otp_code'] = otp_code
                        request.session['otp_user_id'] = user.id
                        request.session['otp_expiry'] = (timezone.now() + timezone.timedelta(minutes=5)).isoformat()
                        context.update({'message': 'OTP sent to your email. Please enter it below.', 'class': 'alert-info'})
                        context['show_otp'] = True
                        context['email'] = email
                        context['password'] = password
                    else:
                        context.update({'message': 'User account is inactive.', 'class': 'alert-danger'})
                else:
                    context.update({'message': 'Invalid Login Details!', 'class': 'alert-danger'})
            else:
                context.update({'message': 'Please enter email and password.', 'class': 'alert-danger'})

    return render(request, 'login.html', context)

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def otp_verification(request):
    context = {}
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        otp_code = request.session.get('otp_code')
        otp_user_id = request.session.get('otp_user_id')
        otp_expiry_str = request.session.get('otp_expiry')

        if not otp_code or not otp_user_id or not otp_expiry_str:
            context['message'] = 'OTP session expired. Please login again.'
            context['class'] = 'alert-danger'
            return render(request, 'otp_verification.html', context)

        otp_expiry = timezone.datetime.fromisoformat(otp_expiry_str)
        if timezone.now() > otp_expiry:
            context['message'] = 'OTP expired. Please login again.'
            context['class'] = 'alert-danger'
            return render(request, 'otp_verification.html', context)

        if otp_input == otp_code:
            from django.contrib.auth.models import User
            user = User.objects.get(id=otp_user_id)
            login(request, user)
            # Clear OTP session data
            del request.session['otp_code']
            del request.session['otp_user_id']
            del request.session['otp_expiry']
            return redirect('dashboard')
        else:
            context['message'] = 'Invalid OTP. Please try again.'
            context['class'] = 'alert-danger'

    return render(request, 'otp_verification.html', context)


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


from restaurants.models import Restaurant

def dashboard(request):
    context = {}
    login_user = get_object_or_404(User, id=request.user.id)
    # fetch login user's details
    profile = Profile.objects.get(user__id=request.user.id)
    context['profile'] = profile

    # update profile
    if "update_profile" in request.POST:
        print("file=", request.FILES)
        name = request.POST.get('name')
        contact = request.POST.get('contact_number')
        add = request.POST.get('address')

        profile.user.first_name = name
        profile.user.save()
        profile.contact_number = contact
        profile.address = add

        if "profile_pic" in request.FILES:
            pic = request.FILES['profile_pic']
            profile.profile_pic = pic
        profile.save()
        context['status'] = 'Profile updated successfully!'

    # Change Password
    if "change_pass" in request.POST:
        c_password = request.POST.get('current_password')
        n_password = request.POST.get('new_password')

        check = login_user.check_password(c_password)
        if check == True:
            login_user.set_password(n_password)
            login_user.save()
            login(request, login_user)
            context['status'] = 'Password Updated Successfully!'
        else:
            context['status'] = 'Current Password Incorrect!'

    # My Orders
    orders = Order.objects.filter(customer__user__id=request.user.id).order_by('-id')
    context['orders'] = orders
    return render(request, 'dashboard_test.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import OrderForm
from products.models_cart import Cart, CartItem



def payment_done(request):
    order_id = request.session.get('order_id')
    order_obj = Order.objects.get(id=order_id)
    order_obj.status = 'DELIVERED'
    order_obj.save()

    return render(request, 'payment_successfull.html')


def payment_cancel(request):
    # remove comment to delete cancelled order
    order_id = request.session.get('order_id')
    Order.objects.get(id=order_id).delete()

    return render(request, 'payment_failed.html')


import requests

import requests
from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
# Removed import of Order as it does not exist in products.models

def order_status_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    status_history = order.status_history.all().order_by('updated_at')
    return render(request, 'order_tracking.html', {
        'order_id': order.id,
        'current_status': order.status,
        'status_history': status_history,
    })

from django.contrib.auth.decorators import login_required
from django.contrib import messages

def create_order_status_history(order, status):
    from products.models_order import OrderStatusHistory
    OrderStatusHistory.objects.create(order=order, status=status)

# Update order creation and status update logic to create OrderStatusHistory entries

from products.models_order import Order

from django.contrib.auth.decorators import login_required

@login_required
def checkout(request):
    user = request.user
    cart = None
    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        cart = None

    if cart is None or cart.items.count() == 0:
        messages.info(request, "Your cart is empty.")
        return redirect('view_cart')

    items = cart.items.select_related('dish').all()
    total_price = 0
    for item in items:
        item.subtotal = item.dish.discounted_price * item.quantity
        total_price += item.subtotal

    if request.method == 'POST':
        # Create order for the user with cart items
        from products.models_order import Order
        from products.models_order import OrderStatusHistory

        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            messages.error(request, "Please update your profile with address before placing order.")
            return redirect('view_cart')

        order = Order(customer=profile, item_name="Multiple Items")
        order.save()
        inv = f'INV0000-{order.id}'
        order.invoice_id = inv
        order.status = 'PENDING_DELIVERY'
        order.save()

        # Create order status history
        OrderStatusHistory.objects.create(order=order, status=order.status)

        # Clear cart items
        cart.items.all().delete()

        # Store order id in session for payment_done
        request.session['order_id'] = order.id

        messages.success(request, "Order placed successfully. Thank you for your order!")
        return redirect('payment_done')

    context = {
        'cart': cart,
        'items': items,
        'total_price': total_price,
    }
    return render(request, 'checkout.html', context)

@login_required
def single_dish(request, id):
    dish = get_object_or_404(Dish, id=id)
    context = {'dish': dish}

    try:
        cust = Profile.objects.get(user__id=request.user.id)
    except Profile.DoesNotExist:
        cust = None

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']

            # Check if address is updated before placing order
            if cust is None or not cust.address or cust.address.strip() == "":
                messages.error(request, "Order cannot be placed. Please update your address in the dashboard.")
                return redirect('dish', id=id)

            # Create order
            order = Order(customer=cust, item_name=dish.name)
            order.save()
            inv = f'INV0000-{order.id}'
            order.invoice_id = inv

            if payment_method == 'COD':
                order.status = 'PENDING_DELIVERY'
                order.save()
                create_order_status_history(order, order.status)
                request.session['order_id'] = order.id
                messages.success(request, "Order placed successfully. Pay on delivery.")
                return redirect('payment_done')
            elif payment_method == 'CARD':
                # Card details are validated by form
                order.status = 'PAID'
                order.save()
                create_order_status_history(order, order.status)
                request.session['order_id'] = order.id
                messages.success(request, "Payment successful. Order placed.")
                return redirect('payment_done')
            else:
                messages.error(request, "Invalid payment method.")
        else:
            messages.error(request, "Please correct the errors below.")
            # Add debug info for form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = OrderForm()

    context['form'] = form

    return render(request, 'dish.html', context)

def payment_done(request):
    order_id = request.session.get('order_id')
    if not order_id:
        messages.error(request, "No order found in session.")
        return redirect('view_cart')
    try:
        order_obj = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('view_cart')

    order_obj.status = 'DELIVERED'
    order_obj.save()
    create_order_status_history(order_obj, order_obj.status)

    return render(request, 'payment_successfull.html')

@login_required
def add_to_cart(request, dish_id):
    if request.method == 'POST':
        user = request.user
        dish = get_object_or_404(Dish, id=dish_id)
        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, dish=dish)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        messages.success(request, f"Added {dish.name} to your cart.")
        return redirect('view_cart')  # Redirect to cart page
    else:
        return redirect('dish', id=dish_id)
