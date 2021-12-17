from django.urls import path
from .views import LogIn, TokenRefresh

urlpatterns = [
    path('login/', LogIn.as_view()),
    path('refresh/', TokenRefresh.as_view()),
]
