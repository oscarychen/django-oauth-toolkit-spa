from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from oauth_toolkit_spa.settings import oauth2_settings
from oauth2_provider.models import get_application_model
from oauth2_provider.views import ProtectedResourceView

Application = get_application_model()
UserModel = get_user_model()


# mocking a protected resource view
class ResourceView(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        return "This is a protected resource"


class BaseTest(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = UserModel.objects.create_user("test_user", "tester@example.com", "123456")
        self.app = Application.objects.create(
            name="test_client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_PASSWORD,
        )
        self.access_token = None

    def tearDown(self) -> None:
        self.user.delete()
        self.app.delete()

    def _get_response_access_token(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.data)
        # self.access_token = response.data['access_token']
        return response.data['access_token']

    def _check_response_refresh_token(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertIn(oauth2_settings.REFRESH_COOKIE_NAME, response.cookies)
        refresh_token_cookie = response.cookies[oauth2_settings.REFRESH_COOKIE_NAME]
        self.assertTrue(refresh_token_cookie['httponly'])
        self.assertTrue(refresh_token_cookie['secure'])
        self.assertEqual(refresh_token_cookie['path'], oauth2_settings.REFRESH_COOKIE_PATH)
        self.assertEqual(refresh_token_cookie['max-age'], oauth2_settings.REFRESH_TOKEN_EXPIRE_SECONDS)
        self.assertEqual(refresh_token_cookie['samesite'], 'strict')

    @staticmethod
    def _print(v):
        print("$$$$$$$ DEBUG $$$$$")
        print(v)
        assert False


class TestClientResourcePasswordBased(BaseTest):

    def test_client_resource_password_based(self):
        access_token = self._log_in()
        self._validate_access_token(access_token)

        # token refresh should cause the access token previous associated with the refresh token to be removed
        access_token_2 = self._token_refresh()
        self._validate_access_token(access_token_2)
        self._check_access_token_is_invalid(access_token)

        self._log_off()
        self._check_access_token_is_invalid(access_token_2)

        # check log off everywhere revokes all outstanding tokens
        access_token_3 = self._log_in()
        access_token_4 = self._log_in()
        self._log_off_everywhere()
        self._check_access_token_is_invalid(access_token_3)
        self._check_access_token_is_invalid(access_token_4)

    def _log_in(self):
        """Log in sequence."""
        response = self.client.post(f"{oauth2_settings.REFRESH_COOKIE_PATH}/login/", {
            "username": "test_user",
            "password": "123456",
            "grant_type": Application.GRANT_PASSWORD,
            "client_id": self.app.client_id
        })
        access_token = self._get_response_access_token(response)
        self._check_response_refresh_token(response)
        return access_token

    def _token_refresh(self):
        """Obtain new access token using refresh token"""
        response = self.client.post(f"{oauth2_settings.REFRESH_COOKIE_PATH}/refresh/", {
            "client_id": self.app.client_id
        })
        access_token = self._get_response_access_token(response)
        return access_token

    def _validate_access_token(self, access_token):
        """Use access token to access a fake resource."""
        auth_headers = {
            "HTTP_AUTHORIZATION": "Bearer " + access_token,
        }
        request = self.factory.get("/fake-resource", **auth_headers)
        request.user = self.user

        view = ResourceView.as_view()
        response = view(request)
        self.assertEqual(response, "This is a protected resource")

    def _check_access_token_is_invalid(self, access_token):
        """Check that access token cannot access a fake resource."""
        auth_headers = {
            "HTTP_AUTHORIZATION": "Bearer " + access_token,
        }
        request = self.factory.get("/fake-resource", **auth_headers)
        request.user = self.user

        view = ResourceView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 403)

    def _log_off(self):
        """Log off"""
        self.client.post(f"{oauth2_settings.REFRESH_COOKIE_PATH}/logoff/", {
            "client_id": self.app.client_id
        })

    def _log_off_everywhere(self):
        """Log off everywhere by revoking all refresh token and access tokens."""
        self.client.post(f"{oauth2_settings.REFRESH_COOKIE_PATH}/logoff-everywhere/", {
            "username": "test_user",
            "password": "123456",
            "grant_type": Application.GRANT_PASSWORD,
            "client_id": self.app.client_id
        })
