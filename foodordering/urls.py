from django.contrib import admin
from django.urls import path, include
from products import views 
from django.conf import settings 
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('',views.index,name="index"),
    path('contact/',views.contact_us,name="contact"),
    path('about/',views.about,name="about"),
    path('team/',views.team_members,name="team"),
    path('dishes/',views.all_dishes,name="all_dishes"),
    path('register/',views.register,name="register"),
    path('check_user_exists/',views.check_user_exists,name="check_user_exist"),
    path('login/', views.signin, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('dish/<int:id>/', views.single_dish, name='dish'),
    path('order_status/<int:order_id>/', views.order_status_view, name='order_status'),

    # Added dummy payment URLs
    path('payment_done/', views.payment_done, name='payment_done'),
    path('payment_cancel/', views.payment_cancel, name='payment_cancel'),

    path('restaurants/', include('restaurants.urls')),
    path('book-table/', views.book_table, name='book_table'),

    # Cart URLs
    path('add-to-cart/<int:dish_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),

    # Redirect accounts/login/ to login/
    path('accounts/login/', RedirectView.as_view(url='/login/', permanent=False)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]+static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
