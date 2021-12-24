from rest_framework.test import APIRequestFactory
from django.test import TestCase
from django.contrib.auth import get_user_model
from oauth_toolkit_cookie_refresh.settings import oauth2_settings
from oauth2_provider.models import get_application_model
from http.cookies import SimpleCookie

Application = get_application_model()
UserModel = get_user_model()


class TestAuthViews(TestCase):

    def setUp(self) -> None:
        self.user = UserModel.objects.create_user("test_user", "tester@example.com", "123456")
        self.app = Application.objects.create(
            name="test_client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_PASSWORD,
        )
        self.refresh_token = None
        self.access_token = None

    def tearDown(self) -> None:
        self.user.delete()
        self.app.delete()

    def test_log_in(self):
        response = self.client.post(f"{oauth2_settings.REFRESH_COOKIE_PATH}/login/",
                                    {
                                        "username": "test_user",
                                        "password": "123456",
                                        "grant_type": "password",
                                        "client_id": self.app.client_id
                                    }
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.data)
        access_token = response.data["access_token"]
        self.access_token = access_token
        self.assertIn(oauth2_settings.REFRESH_COOKIE_NAME, response.cookies)
        refresh_token_cookie = response.cookies[oauth2_settings.REFRESH_COOKIE_NAME]
        self.refresh_token = refresh_token_cookie._value

        # check refresh token cookie attributes
        self.assertTrue(refresh_token_cookie['httponly'])
        self.assertTrue(refresh_token_cookie['secure'])
        self.assertEqual(refresh_token_cookie['path'], oauth2_settings.REFRESH_COOKIE_PATH)
        self.assertEqual(refresh_token_cookie['max-age'], oauth2_settings.REFRESH_TOKEN_EXPIRE_SECONDS)
        self.assertEqual(refresh_token_cookie['samesite'], 'strict')

    # def test_token_refresh(self):
    #     pass
    #     response = self.client.post(f"{oauth2_settings.REFRESH_COOKIE_PATH}/refresh/")
    #
    # def test_log_off(self):
    #     pass
    #     response = self.client.post()
    #
    # def test_log_off_everywhere(self):
    #     pass

    def _print(self, v):
        print("$$$$$$$ DEBUG $$$$$")
        print(v)
        assert False
