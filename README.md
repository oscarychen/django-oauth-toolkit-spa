# Django-oauth-toolkit-cookie-refresh

[![CI tests](https://github.com/oscarychen/django-oauth-toolkit-cookie-refresh/actions/workflows/test.yml/badge.svg)](https://github.com/oscarychen/django-oauth-toolkit-cookie-refresh/actions/workflows/test.yml)
[![Package Downloads](https://img.shields.io/pypi/dm/django-oauth-toolkit-cookie-refresh)](https://pypi.org/project/django-oauth-toolkit-cookie-refresh/)

Django-oauth-toolkit-cookie-refresh is a Django app to that provides REST authentication endpoints which uses refresh
token in httpOnly cookie. It relies on [Django REST framework](https://github.com/encode/django-rest-framework)
and [Django Oauth Toolkit](https://github.com/jazzband/django-oauth-toolkit).

## Motivation

The django-oauth-toolkit by default sends back access token and refresh token both in response body. This presents a 
dilemma for web developers as to where to store/persist each token:

- Web storage (local storage and session storage) is accessible through Javascript on the same domain, this presents an 
opportunity for malicious scripts running on your site to carry out XSS against your user clients, which makes web 
storage not ideal for storing either access or refresh tokens. There are a large number of scenarios where XSS can take
place, and a number of ways to mitigate them. you can read more about XSS [here](https://gist.github.com/oscarychen/352d60c1a2e3727d444c94b5959bb6f6).
- Cookies with `HttpOnly` flag are not accessible by Javascript and therefore not vulnerable to XSS, however they may be
the target of CSRF attack because of ambient authority, where cookies may be attached to requests automatically. Even 
though a malicious website carrying out a CSRF has no way of reading the response of the request which is made on behalf 
of a user, they may be able to make changes to user data resources if such endpoints exist. This makes `HttpOnly` 
cookies unsuited for storing access token. There are several ways to mitigate CSRF, such as setting the `SameSite`
attribute of a cookie to "Lax" or "Strict", and using anti-CSRF token. You can read more about CSRF [here](https://gist.github.com/oscarychen/ce189b2fef1f8ff7eac51a72fed34960).

In addition to various XSS and CSRF mitigation techniques, this package deploys access token and refresh token for web 
apps in a specific way that broadly hardens application security against these attacks:
- Access tokens, are as usual, send back to clients in response body. It is expected that you would design your frontend
application to not persist access tokens anywhere. They are short-lived and only used by the SPA in memory, and are 
tossed as soon as the user close the browser tab. This way, the access token cannot be utilized in a CSRF attack against
your application.
- Refresh tokens, are sent back to client in a `HttpOnly` cookie header that the client browser sees but inaccessible 
by your own frontend application. This way, the refresh token is not subject to any XSS attack against your application.
While CSRF is possible, the attacker cannot use this mechanism to make modification to your resources even is a CSRF 
attack is successfully carried out. It is important to note that in CSRF, the attacker cannot read the response even
when they successfully make the malicious request to your API endpoint; the worst they can do is to refresh the token
on user's behalf, and no damage can be done. The refresh token cookie would also typically have `domain` and `path`
attributes specified, so that browsers should only attach them with request to your domain and specific url path
used for refreshing the tokens, therefore reducing attack surfaces further.

## Quick start

Install using pip:

```
pip install django-oauth-toolkit-spa
```

Or, install from source:

Set
up [django-oauth-toolkit and django REST framework](https://django-oauth-toolkit.readthedocs.io/en/latest/rest-framework/getting_started.html#step-1-minimal-setup) if you haven't already:

```python
INSTALLED_APPS = (
    'django.contrib.admin',
    ...,
    'oauth2_provider',
    'rest_framework',
)
```

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    )
}
```

Include the oauth_toolkit_spa URLconf in your project urls.py:

```python
path('auth/', include('oauth_toolkit_spa.urls')),
```

## Settings

django-oauth-toolkit's settings are largely extended and used, except few default values have been overwritten. These
settings are used as default unless explicitly specified:

```
"ACCESS_TOKEN_EXPIRE_SECONDS": 300,
"REFRESH_TOKEN_EXPIRE_SECONDS": 36000,
"REFRESH_COOKIE_NAME": "refresh_token",
"REFRESH_COOKIE_PATH": "/auth"
```

You can modify these settings by specifying them in the settings for django-oauth-toolkit:

```python
OAUTH2_PROVIDER = {
    ...,
    "ACCESS_TOKEN_EXPIRE_SECONDS": 300,
    "REFRESH_TOKEN_EXPIRE_SECONDS": 36000,
    "REFRESH_COOKIE_NAME": "refresh_token",
    "REFRESH_COOKIE_PATH": "/auth",
    ...
}
```

If you want to use a different path for authentication than the default path, you should provide the setting
in `REFRESH_COOKIE_PATH`, using a string with leading slash `/`; while provide the same path in URLconf but with a
trailing slash `/`.
