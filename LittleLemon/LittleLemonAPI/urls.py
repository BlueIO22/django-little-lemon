from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', views.home),
    path('menu-items', views.menu_items),
    path('menu-items/<int:pk>', views.menu_item),
    path('category', views.categories),
    path('category/<int:pk>', views.category),
    path('orders', views.orders),
    path('orders/<int:pk>', views.order),
    path('cart', views.cart),
    path('groups/manager/users', views.managers),
    path('groups/delivery-crew/users', views.delivery_crew),
    path('register', views.customer),
    path('me', views.me),
    path('token/', TokenObtainPairView.as_view(), name="token_obtain"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh")
]
