# Django-oauth-toolkit-cookie-refresh

Django-oauth-toolkit-cookie-refresh is a Django app to that provides REST authentication endpoints which uses refresh
token in httpOnly cookie. It relies on [Django REST framework](https://github.com/encode/django-rest-framework)
and [Django Oauth Toolkit](https://github.com/jazzband/django-oauth-toolkit).

#### Motivation

I was using django-oauth-toolkit in a project, but I wanted the refresh tooken to be handled by a HttpOnly cookie, while
having the access token to be continue sent via request/response body.

## Quick start

Install from source:

```commandline
pip install git+https://github.com/oscarychen/django-oauth-toolkit-cookie-refresh.git
```

Set
up [django-oauth-toolkit and django REST framework](https://django-oauth-toolkit.readthedocs.io/en/latest/rest-framework/getting_started.html#step-1-minimal-setup):

```python
INSTALLED_APPS = (
    'django.contrib.admin',
    ...
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

Include the oauth_toolkit_cookie_refresh URLconf in your project urls.py:

```python
    path('auth/', include('oauth_toolkit_cookie_refresh.urls')),
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
    ...
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

## Development

To continue develope this package, I've included a `requirements.txt` and `env_setup.sh` to help you get up and running.

With the appropriate Python(ie: Python 3.8), run the following to set up a Python virtual environment in project
directory:

```commandline
source env_setup.py
```

which also creates a `activate.sh`. and then activate the environment by running:

```commandline
source activate.sh
```

To build this package:

```commandline
python setup.py sdist
```

To include this package symbolically in another environment:

```commandline
pip install -e PATH_TO_PACKAGE_DIRECTORY
```

Automated testing

```commandline
tox
```