"""
Extending Django oauth toolkit settings.
"""
from oauth2_provider.settings import DEFAULTS, OAuth2ProviderSettings, IMPORT_STRINGS, MANDATORY
from django.conf import settings


MODIFIED_DEFAULTS = {
    **DEFAULTS,
    "ACCESS_TOKEN_EXPIRE_SECONDS": 300,
    "REFRESH_TOKEN_EXPIRE_SECONDS": 36000,
    "REFRESH_COOKIE_NAME": "refresh_token",
    "REFRESH_COOKIE_PATH": "/auth"
}

USER_SETTINGS = getattr(settings, "OAUTH2_PROVIDER", None)

oauth2_settings = OAuth2ProviderSettings(USER_SETTINGS, MODIFIED_DEFAULTS, IMPORT_STRINGS, MANDATORY)
