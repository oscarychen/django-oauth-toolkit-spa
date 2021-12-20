from rest_framework.views import APIView
from rest_framework import permissions
from .mixins import OAuthToolKitMixin


class LogIn(APIView, OAuthToolKitMixin):
    '''Log in API endpoint'''
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        return self.get_login_response(request)


class TokenRefresh(APIView, OAuthToolKitMixin):
    '''Token refresh API endpoint'''
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        return self.get_refresh_response(request)


class LogOff(APIView, OAuthToolKitMixin):
    '''Log off API endpoint'''
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return self.get_logoff_response(request)
