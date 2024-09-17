from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', views.home, name="home"),
    path('about/', views.about, name="about"),
    path('book/', views.book, name="book"),
    path('reservations/', views.reservations, name="reservations"),
    path('menu/', views.menu, name="menu"),
    path('menu_item/<int:pk>/', views.display_menu_item, name="menu_item"),  
    path('bookings', views.bookings, name='bookings'), 
    path('api/menu-items', views.menu_items),
    path('api/menu-items/<int:pk>', views.menu_item),
    path('api/category', views.categories),
    path('api/category/<int:pk>', views.category),
    path('api/orders', views.orders),
    path('api/orders/<int:pk>', views.order),
    path('api/cart', views.cart),
    path('api/groups/manager/users', views.managers),
    path('api/groups/delivery-crew/users', views.delivery_crew),
    path('api/register', views.customer),
    path('api/token/', TokenObtainPairView.as_view(), name="token_obtain"),
    path('api/token/refresh/', TokenRefreshView.as_view(), name="token_refresh")
]
