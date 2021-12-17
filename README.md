# Django-oauth-toolkit-cookie-refresh

Django-oauth-toolkit-cookie-refresh is a Django app to that provides authentication endpoints which uses refresh token in httpOnly cookie.

#### Motivation

I was using django-oauth-toolkit in a project, but I wanted the refresh tooken to handled by a HttpOnly cookie.

## Quick start

Include the oauth_toolkit_cookie_refresh URLconf in your project urls.py like this:

```
    path('auth/', include('oauth_toolkit_cookie_refresh.urls')),
```

## Development

To continue develope this package, I've included a `requirements.txt` and `env_setup.sh` to help you get up and running.

With the appropriate Python environment activated, run the following to set up a Python virtual environment in project directory:

```
source env_setup.py
```

which also creates a `activate.sh`.
and then activate the environment by running:

```
source activate.sh
```

To build this package:

```
python setup.py sdist
```

To include this package symbolically in another environment:

```
pip install -e PATH_TO_PACKAGE_DIRECTORY
```
