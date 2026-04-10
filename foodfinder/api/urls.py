from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import health, register, food_search, my_search_history

urlpatterns = [
   path('health/', health, name='health'),
   path('auth/register/', register, name='register'),
   path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
   path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   path('food/search/', food_search, name='food_search'),
   path('my-search-history/', my_search_history, name='my_search_history'),
]




