from rest_framework.test import APIRequestFactory
from django.test import TestCase
from django.contrib.auth import get_user_model
from oauth_toolkit_cookie_refresh.settings import oauth2_settings
from oauth2_provider.models import get_application_model


factory = APIRequestFactory()
request = factory.post('')
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

    def tearDown(self) -> None:
        self.user.delete()
        self.app.delete()

    def test_log_in(self):
        self.client.login(username="test_user", password="123456")

    def test_log_off(self):
        pass

    def test_log_off_everywhere(self):
        pass
