from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import health, register, register_options, food_search, my_search_history, my_profile, LoginView

urlpatterns = [
   path('health/', health, name='health'),
   path('auth/register/', register, name='register'),
   path('auth/register/options/', register_options, name='register_options'),
   path('auth/profile/', my_profile, name='my_profile'),
   path('auth/login/', LoginView.as_view(), name='token_obtain_pair'),
   path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   path('food/search/', food_search, name='food_search'),
   path('my-search-history/', my_search_history, name='my_search_history'),
]




