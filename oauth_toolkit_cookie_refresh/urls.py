from django.urls import path
from .views import LogIn, TokenRefresh, LogOff

urlpatterns = [
    path('login/', LogIn.as_view()),
    path('refresh/', TokenRefresh.as_view()),
    path('logoff/', LogOff.as_view())
]
