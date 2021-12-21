from datetime import timedelta
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from .settings import oauth2_settings
from oauth2_provider.models import get_access_token_model, get_refresh_token_model, get_application_model
from oauthlib import common
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import authenticate, login
from .serializers import RefreshSerializer, LogInSerializer
from typing import Union


class OAuthToolKitMixin:

    def get_login_response(self, request):
        '''Returns log in response when user sign in using username and password.'''
        access_token, refresh_token = self.get_user_access_refresh_tokens(request)
        response_body = self._make_response_body(access_token)
        response = Response(response_body, status=status.HTTP_200_OK)
        return self._set_cookie_header_in_response(response, refresh_token.token)

    def get_logoff_response(self, request):
        '''Revokes refresh token and associated access token.'''
        refresh_token = self._get_refresh_token_instance(request, raise_exception=False)
        if refresh_token is not None:
            refresh_token.revoke()
        return self._set_delete_cookie_response()

    def get_logoff_everywhere_response(self, request):
        '''Revokes all refresh tokens associated with user'''
        refresh_tokens, access_tokens = self._get_all_tokens(request)
        access_tokens.delete()
        refresh_tokens.update(revoked=timezone.now(), access_token=None)

        return self._set_delete_cookie_response()

    def get_refresh_response(self, request):
        '''Returns token refresh response when user refreshes using a refresh token.'''
        refresh_token = self._get_refresh_token_instance(request)
        if refresh_token is None:
            return self._set_delete_cookie_response(status=status.HTTP_401_UNAUTHORIZED)

        refresh_token.access_token.revoke()
        access_token = get_access_token_model()(user=refresh_token.user, scope='', expires=self._get_access_token_expires_time(),
                                                token=common.generate_token(), application=refresh_token.application)
        access_token.save()
        refresh_token.access_token = access_token
        refresh_token.save()
        response_body = self._make_response_body(access_token)

        return Response(response_body, status=status.HTTP_200_OK)

    def _get_refresh_token_instance(self, request, raise_exception=True):
        client_id = self._get_request_client_id(request)
        token = self._get_token_from_cookie(request, raise_exception)
        if not token:
            return

        refresh_token_creation_time = timezone.now() - timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS or 36000)
        try:
            refresh_token = get_refresh_token_model().objects.get(token=token, application__client_id=client_id,
                                                                  revoked__isnull=True, created__gt=refresh_token_creation_time)
            return refresh_token
        except:
            if raise_exception is True:
                raise AuthenticationFailed()

    def _get_request_client_id(self, request, raise_exception=True) -> str:
        '''Get client_id from request'''
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=raise_exception)
        client_id = serializer.validated_data['client_id']
        return client_id

    def _get_token_from_cookie(self, request, raise_exception=True) -> Union[str, None]:
        '''Reads refresh token from cookie.'''
        try:
            token = request.get_signed_cookie(oauth2_settings.REFRESH_COOKIE_NAME, salt="token_cookie_salt")
        except:
            if raise_exception is True:
                raise AuthenticationFailed()
            else:
                return
        return token

    def _get_refresh_token_expires_time(self):
        return timezone.now() + timedelta(seconds=oauth2_settings.REFRESH_TOKEN_EXPIRE_SECONDS or 36000)

    def _get_access_token_expires_time(self):
        return timezone.now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS or 600)

    def _make_response_body(self, access_token):
        return {
            "access_token": access_token.token,
            "user": {"username": access_token.user.username, "email": access_token.user.email}
        }

    def get_user_access_refresh_tokens(self, request):
        '''
        Authenticates username and password, returns oauth2_provider AccessToken and RefreshToken instances in a tuple.
        '''
        serializer = LogInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = authenticate(request, username=validated_data['username'], password=validated_data['password'])

        if user is None:
            raise AuthenticationFailed()

        login(request, user)

        application = get_application_model().objects.get(client_id=validated_data['client_id'])
        access_token = get_access_token_model()(user=user, scope='', expires=self._get_access_token_expires_time(),
                                                token=common.generate_token(), application=application)
        access_token.save()

        refresh_token = get_refresh_token_model()(
            user=user,
            token=common.generate_token(),
            application=application,
            access_token=access_token
        )
        refresh_token.save()
        return access_token, refresh_token

    def _get_all_tokens(self, request):
        '''Returns oustanding refresh token and access token instances.'''
        serializer = LogInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        client_id = validated_data['client_id']
        user = authenticate(request, username=validated_data['username'], password=validated_data['password'])

        if user is None:
            raise AuthenticationFailed()

        refresh_tokens = get_refresh_token_model().objects.filter(
            user=user, application__client_id=client_id, revoked__isnull=True)
        access_tokens = get_access_token_model().objects.filter(user=user)

        return refresh_tokens, access_tokens

    def _set_cookie_header_in_response(self, response, refresh_token):
        '''Sets refresh token as samesite HttpOnly cookie in header'''
        response.set_signed_cookie(key=oauth2_settings.REFRESH_COOKIE_NAME, value=refresh_token, salt="token_cookie_salt", expires=self._get_refresh_token_expires_time(),
                                   httponly=True, samesite='strict', secure=not settings.DEBUG, path=oauth2_settings.REFRESH_COOKIE_PATH)
        return response

    def _set_delete_cookie_response(self, status=status.HTTP_200_OK):
        response = Response(status=status)
        response.delete_cookie(key=oauth2_settings.REFRESH_COOKIE_NAME, path=oauth2_settings.REFRESH_COOKIE_PATH)
        return response
